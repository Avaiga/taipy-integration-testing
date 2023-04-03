
def assert_true_after_time(assertion, msg=None, time=120):
    from datetime import datetime
    from time import sleep

    start = datetime.now()
    while (datetime.now() - start).seconds < time:
        sleep(1)  # Limit CPU usage
        try:
            if assertion():
                return
        except BaseException as e:
            print("Raise : ", e)
            continue
    if msg:
        print(msg)
    assert assertion()
