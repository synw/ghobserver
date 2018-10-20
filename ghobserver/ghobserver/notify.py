import os
import notify2


def notify(title, msg, persist=False, timeout=10000):

    dirpath = os.path.dirname(os.path.realpath(__file__))
    icon_path = dirpath + "/static/img/notification.png"
    
    # initialise the d-bus connection
    notify2.init("Github observer notifier")
 
    # create Notification object
    n = notify2.Notification(title, msg, icon=icon_path)
    n.set_category("device")
        
    # Set the urgency level
    level = notify2.URGENCY_NORMAL
    if persist is True:
        level = notify2.URGENCY_CRITICAL
    n.set_urgency(level)
        
    # Set the timeout
    n.set_timeout(timeout)
    n.show()
