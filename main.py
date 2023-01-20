from Scheduler.scheduler import Scheduler


def main():
    scheduler = Scheduler("config.json")
    scheduler.run()


if __name__ == "__main__":
    main()
