
def manager_user(user):
    return user.groups.filter(name="Manager").exists()

def delivery_crew_user(user):
    return user.groups.filter(name="Delivery crew").exists()