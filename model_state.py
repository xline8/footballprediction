#!/usr/bin/env python3
"""model_state.py — Sistem persistensi dan caching untuk model Dixon-Coles.

Menyimpan state model (rating tim, rho, konfigurasi) secara per divisi.
Mendukung:
- Save/load model state
- Incremental updates
- Version control (timestamp, last fit date)
"""

import os
import pickle
import json
from datetime import datetime, date
from typing import Optional, Tuple, Dict, Any
from collections import defaultdict

from paths import BASE, MODEL_CACHE

CACHE_DIR = MODEL_CACHE
MAX_TRAIN = 4000
RHO_GRID = (0.0, -0.05, -0.10, -0.15)


class ModelState:
    """Persistensi state model Dixon-Coles per divisi."""

    def __init__(self, div: str):
        self.div = div
        self.version = "1.0"
        self.created_at = datetime.now().isoformat()
        self.updated_at = None
        self.last_fit_date = None  # Tanggal terakhir model di-fit
        self.last_update = None    # Tanggal update terakhir (setelah incremental)
        self.half_life = 270.0     # Default dari config

        # Model parameters
        self.attack: Dict[str, float] = defaultdict(float)  # team -> attack strength
        self.defense: Dict[str, float] = defaultdict(float) # team -> defense Strength
        self.home_advantage: float = 0.28
        self.rho: float = -0.07

        # Training metadata
        self.n_matches_trained: int = 0
        self.training_cutoff: Optional[date] = None
        self.training_window_days: int = 0

        # Cache untuk hasil prediksi
        self._prediction_cache: Dict[Tuple[str, str], Dict] = {}  # (home, away) -> probs
        self._team_list: set = set()
        self._initialized = False

    def save(self, force: bool = False):
        """Simpan state model ke file."""
        if not force and not self.updated_at:
            return  # Hanya save jika ada update

        os.makedirs(CACHE_DIR, exist_ok=True)
        filepath = self._get_filepath()

        # Extract defaultdict ke regular dict untuk serialisasi
        data = {
            "version": self.version,
            "div": self.div,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_fit_date": self.last_fit_date.isoformat() if self.last_fit_date else None,
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "half_life": self.half_life,
            "attack": dict(self.attack),
            "defense": dict(self.defense),
            "home_advantage": self.home_advantage,
            "rho": self.rho,
            "n_matches_trained": self.n_matches_trained,
            "training_cutoff": self.training_cutoff.isoformat() if self.training_cutoff else None,
            "training_window_days": self.training_window_days,
            "initialized": self._initialized
        }

        with open(filepath, 'wb') as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

    def load(self) -> bool:
        """Load state model dari file. Return True jika berhasil."""
        filepath = self._get_filepath()
        if not os.path.exists(filepath):
            return False

        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)

            self.version = data.get("version", self.version)
            self.created_at = data.get("created_at", self.created_at)
            self.updated_at = data.get("updated_at")
            self.last_fit_date = self._parse_date(data.get("last_fit_date"))
            self.last_update = self._parse_date(data.get("last_update"))
            self.half_life = data.get("half_life", self.half_life)
            self.attack = defaultdict(float, data.get("attack", {}))
            self.defense = defaultdict(float, data.get("defense", {}))
            self.home_advantage = data.get("home_advantage", self.home_advantage)
            self.rho = data.get("rho", self.rho)
            self.n_matches_trained = data.get("n_matches_trained", 0)
            self.training_cutoff = self._parse_date(data.get("training_cutoff"))
            self.training_window_days = data.get("training_window_days", 0)
            self._initialized = data.get("initialized", False)
            return True
        except Exception as e:
            print(f"Warning: Gagal load model state {self.div}: {e}")
            return False

    def update_from_model(self, dc_model, fit_date: date, hl: float):
        """Update state dari objek model DC."""
        self.attack = defaultdict(float, dict(dc_model.a))
        self.defense = defaultdict(float, dict(dc_model.d))
        self.home_advantage = dc_model.h
        self.rho = dc_model.rho
        self.half_life = hl
        self.last_fit_date = fit_date
        self.last_update = datetime.now()
        self._initialized = True
        self._team_list = set(self.attack.keys()) | set(self.defense.keys())

        # Update training metadata
        cutoff_str = fit_date.isoformat()
        if self.training_cutoff:
            self.training_window_days = abs((fit_date - self.training_cutoff).days)
        self.training_cutoff = fit_date

        # Mark cache as stale
        self._prediction_cache.clear()
        self.save()

    def incremental_update(self, team: str, opp: str, goals_for: int,
                           goals_against: int, is_home: bool, weight: float):
        """Update rating tim secara inkremental berdasarkan hasil pertandingan baru."""
        if not self._initialized:
            return

        # Simple Elo-like adjustment
        # attack rating adjustment
        k_factor = 0.7 * weight
        exp_goals = self._expected_goals(team, opp, is_home)

        # Update attack/defense
        if is_home:
            self.attack[team] += k_factor * ((goals_for - exp_goals[0]) / max(exp_goals[0], 0.1))
            self.defense[opp] += k_factor * ((goals_against - exp_goals[1]) / max(exp_goals[1], 0.1))
        else:
            self.attack[team] += k_factor * ((goals_for - exp_goals[1]) / max(exp_goals[1], 0.1))
            self.defense[opp] += k_factor * ((goals_against - exp_goals[0]) / max(exp_goals[0], 0.1))

        self.last_update = datetime.now()
        self.n_matches_trained += 1
        self._prediction_cache.clear()  # Clear prediction cache

    def _expected_goals(self, team: str, opp: str, is_home: bool) -> Tuple[float, float]:
        """Estimate expected goals (home_goals, away_goals)."""
        import math
        lh = math.exp(self.attack[team] + self.defense[opp] + self.home_advantage)
        la = math.exp(self.attack[opp] + self.defense[team])
        return (lh, la) if is_home else (la, lh)

    def get_lambda(self, home: str, away: str) -> Tuple[float, float]:
        """Dapatkan lambda (expected goals) untuk sebuah laga."""
        import math
        lh = math.exp(self.attack[home] + self.defense[away] + self.home_advantage)
        la = math.exp(self.attack[away] + self.defense[home])
        return (max(lh, 0.03), max(la, 0.03))

    def get_known_teams(self) -> set:
        """Dapatkan semua tim yang diketahui model."""
        return self._team_list if self._team_list else (
            set(self.attack.keys()) | set(self.defense.keys()))

    def clear_prediction_cache(self):
        """Hapus cache prediksi (dipanggil saat model di-update)."""
        self._prediction_cache.clear()

    def _get_filepath(self) -> str:
        """Path file state model."""
        return os.path.join(CACHE_DIR, f"model_{self.div}.pkl")

    @staticmethod
    def _parse_date(s: Optional[str]) -> Optional[date]:
        if not s:
            return None
        try:
            return datetime.fromisoformat(s).date()
        except (ValueError, TypeError):
            return None

    def is_stale(self, current_date: date, max_age_days: int = 7) -> bool:
        """Cek apakah model sudah terlalu usang."""
        if not self.last_fit_date:
            return True
        return abs((current_date - self.last_fit_date).days) > max_age_days

    def needs_fit(self, games_history: list, cutoff: date) -> bool:
        """Cek apakah perlu refit (tim baru atau window training berubah)."""
        if not self._initialized:
            return True

        known_teams = self.get_known_teams()
        for game in games_history[-MAX_TRAIN:]:
            if game[0] not in known_teams or game[1] not in known_teams:
                return True

        return False


def load_model_state(div: str) -> ModelState:
    """Load atau buat baru ModelState untuk divisi."""
    state = ModelState(div)
    state.load()
    return state


def save_model_state(state: ModelState):
    """Simpan state model."""
    state.save(force=True)


def clear_model_cache(div: str = None):
    """Hapus cache model untuk satu divisi atau semua."""
    if div:
        path = os.path.join(CACHE_DIR, f"model_{div}.pkl")
        if os.path.exists(path):
            os.remove(path)
    else:
        if os.path.exists(CACHE_DIR):
            for f in os.listdir(CACHE_DIR):
                if f.endswith('.pkl'):
                    os.remove(os.path.join(CACHE_DIR, f))


def get_model_cache_info() -> dict:
    """Dapatkan info cache model."""
    info = {}
    if not os.path.exists(CACHE_DIR):
        return {"exists": False}

    files = [f for f in os.listdir(CACHE_DIR) if f.endswith('.pkl')]
    info["exists"] = True
    info["cache_dir"] = CACHE_DIR
    info["n_models"] = len(files)
    info["models"] = []

    for f in sorted(files):
        path = os.path.join(CACHE_DIR, f)
        size = os.path.getsize(path)
        stat = ModelState(f.replace("model_", "").replace(".pkl", ""))
        if stat.load():
            info["models"].append({
                "div": stat.div,
                "file": f,
                "size_kb": round(size / 1024, 1),
                "initialized": stat._initialized,
                "last_fit": stat.last_fit_date.isoformat() if stat.last_fit_date else None,
                "n_teams": len(stat.get_known_teams()),
                "n_matches": stat.n_matches_trained
            })

    return info


if __name__ == "__main__":
    # Test model state
    print("Testing model_state module...")

    # Create and save a test state
    state = ModelState("TEST")
    state.attack["team_a"] = 0.5
    state.defense["team_a"] = -0.3
    state.save(force=True)

    # Load it back
    loaded = load_model_state("TEST")
    print(f"Loaded: {loaded.div}, teams: {list(loaded.get_known_teams())}")
    print(f"Lambda: {loaded.get_lambda('team_a', 'unknown_team')}")

    # Test cache info
    info = get_model_cache_info()
    print(f"Cache info: {json.dumps(info, indent=2)}")

    # Clean up
    clear_model_cache()
    print("Cleaned up test cache")

    print("Done!")
