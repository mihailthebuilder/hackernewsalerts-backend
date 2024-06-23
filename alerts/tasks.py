def send_alerts():
    print("sending alerts")
    return 500


def handle_send_alerts_result(task):
    print(task.result)
