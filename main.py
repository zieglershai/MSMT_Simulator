from Scheduler.scheduler import Scheduler
import os


def main():
    base_path = "/Users/ori/git/MSMT_Simulator/configs/prefetch_2_threads"
    configs = os.listdir(base_path)
    print("running on:", configs)
    for conf in configs:
        scheduler = Scheduler(os.path.join(base_path, conf))
        final_string = scheduler.run()
        out_file = os.path.basename(conf).replace(".json", ".txt")
        out_file = os.path.join("outputs/prefetch_2_threads", out_file)
        with open(out_file, "w") as f:
            f.write(final_string)


if __name__ == "__main__":
    main()
