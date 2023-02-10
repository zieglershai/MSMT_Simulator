from Scheduler.scheduler import Scheduler


def main():
    scheduler = Scheduler("config.json")
    final_string = scheduler.run()
    with open("outputs/final.txt", "w") as f:
        f.write(final_string)


if __name__ == "__main__":
    main()
