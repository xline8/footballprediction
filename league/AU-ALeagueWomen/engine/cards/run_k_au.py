from harness import dev, virgin
import sys
if __name__ == "__main__": virgin() if len(sys.argv)>1 and sys.argv[1]=="virgin" else dev()
