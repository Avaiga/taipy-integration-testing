
def assert_true_after_time(assertion, msg=None, time=120):
    from datetime import datetime
    from time import sleep

    start = datetime.now()
    while (datetime.now() - start).seconds < time:
        print(f"waiting {(datetime.now() - start).seconds} seconds...", end='\r')
        try:
            if assertion():
                print(f"waiting {(datetime.now() - start).seconds} seconds...")
                return
        except BaseException as e:
            print("Raise : ", e)
            sleep(1)  # Limit CPU usage
            continue
    print(f"waiting {(datetime.now() - start).seconds} seconds...")
    if msg:
        print(msg)
    assert assertion()
