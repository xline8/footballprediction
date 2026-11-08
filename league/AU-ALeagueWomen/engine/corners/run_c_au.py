from harness import dev, virgin_read
import sys
if __name__ == "__main__": virgin_read() if len(sys.argv)>1 and sys.argv[1]=="virgin" else dev()
