import argparse, json, os
from harness import run_dev, HERE
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('step',choices=('dev','virgin')); a=p.parse_args(); d=run_dev()
    if a.step=='virgin':
        out={'verdict':'FAIL','virgin_read':False,'reason':'Gate Zero and RS both failed the dev gate; virgin NOT read','read_arms':[],'dev_pass':d['dev_pass'],'clausura_rows_loaded':False}
        json.dump(out,open(os.path.join(HERE,'results_virgin.json'),'w'),indent=2)
