import os
import subprocess
import time

TEST_COUNT = 100

class AverageCounter:

    def __init__(self):
        self.max = 0
        self.min = 2**16
        self.total = 0
        self.count = 0
        self.avg = 0

    def add(self, amount):
        self.total += amount
        self.count += 1
        self.max = max(self.max, amount)
        self.min = min(self.min, amount)
        self.avg = self.total / self.count

    def __str__(self) -> str:
        return f"""
            Average: {self.avg}
            Min: {self.min}
            Max: {self.max}
        """

    def __repr__(self) -> str:
        return self.__str__()

def main():
    max_tpt_avg = AverageCounter()
    worst_fps_avg = AverageCounter()

    print("Compiling C libraries...")
    os.system("./compile.sh")
    print("Compilation done, starting benchmark...")
    time.sleep(0)

    for i in range(1, TEST_COUNT + 1):
        print(f"Starting iteration {i}/{TEST_COUNT}")
        out = subprocess.run("python3 ./main.py", shell=True, capture_output=True, text=True).stdout
        relevant = [i for i in out.split("\n") if i][-2:]
        max_tpt, min_fps = map(float, relevant)
        max_tpt_avg.add(max_tpt)
        worst_fps_avg.add(min_fps)

    print("Longest time per tick:", end="")
    print(max_tpt_avg)
    
    print("-" * 64)

    print("Worst frames per second", end="")
    print(worst_fps_avg)

if __name__ == "__main__":
    main()