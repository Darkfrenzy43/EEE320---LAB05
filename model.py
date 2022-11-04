"""

    Description:

    Provides the model classes representing the state of the OORMS
    system.

    Notes:
        - None for now


    Submitting lab group: OCdt Al-Ansar Mohammed, OCdt Velasco
    Submission date: November 24th, 2022

    Original code by EEE320 instructors.

"""

# ---- Importing built-in Libraries ----
import enum

# ---- Importing from other modules -----

from constants import TABLES, MENU_ITEMS


# ------ Defining Enumerated Constants ------

class Status(enum.IntEnum):
    """ Enumerated constants of type enum.IntEnum with linear values that track the state of a given order
    item when placed within the KitchenView window. See oorms.py/Notes 4 for an in depth explanation.
    With IntEnum, can use int(Status.this_status) to retrieve the value of a given Status enum constant. """

    REQUESTED = -1; # damn, there ain't no elegant way to write this out xD
    PLACED = 0;
    COOKED = 1;
    READY = 2;
    SERVED = 3;


class Restaurant:

    def __init__(self):
        """ Constructor to the Restaurant Class.

        Upon instantiation, retrieves table and menu item data, creates a list of each of the objects
        and stores the lists in instance variables. """
        super().__init__()
        self.tables = [Table(seats, loc) for seats, loc in TABLES]
        self.menu_items = [MenuItem(name, price) for name, price in MENU_ITEMS]
        self.views = []

    def add_view(self, view):
        """ Method adds the RestaurantView object <view> passed through args into the self.views list attribute """
        self.views.append(view)

    def notify_views(self):
        """ Method invokes the update() method on all the views in self.views list - polymorphism example. """
        for view in self.views:
            view.update()


class Table:

    def __init__(self, seats, location):
        """ Constructor to the Table Class.

        <seats> argument refers to the number of seats the Table object to be created will have.
        <location> argument refers to the location the Table object is to placed on the canvas. """
        self.n_seats = seats
        self.location = location
        self.orders = [Order() for _ in range(seats)]


    def has_any_active_orders(self):
        """ Returns True if there are still active orders pending that have not been served.
        If there are none, then obviously returns false. """
        for order in self.orders:
            for item in order.items:
                if item.has_been_ordered() and not item.has_been_served():
                    return True
        return False


    def has_order_for(self, seat):
        """ Function returns a boolean that indicates whether the given seat of number <seat> has ordered yet. """
        return bool(self.orders[seat].items)


    def order_for(self, seat):
        """ Function returns the specific Order object associated with the seat whose
        number <seat> has been passed through the arguments. """
        return self.orders[seat]


class Order:

    def __init__(self):
        """ Constructor for Order object.

        In short, this object is responsible for keeping track of the orders placed by a given
        seat in the restaurant.

        Every chair gets their own Order object associated with it. """
        self.items = []

    def add_item(self, menu_item):
        """ Function simply adds the OrderItem object <menu_item> passed through
        the arguments into the self.items list attribute of the Order object. """
        item = OrderItem(menu_item)
        self.items.append(item)

    def remove_item(self, order_item):
        """ Function simply removes the <item> object passed through args from the self.items list"""
        self.items.remove(order_item)

    def place_new_orders(self):
        """ Function goes through the list attribute self.items of the given Order object and
        sets all OrderItem objects in the list's ordered attribute from False to True. """
        for item in self.unordered_items():
            item.mark_as_ordered()

    def remove_unordered_items(self):
        """ Function removes all the items in the list attribute self.items that have an "unordered" status. """
        for item in self.unordered_items():
            self.items.remove(item)

    def unordered_items(self):
        """ Function returns a list of all OrderItem objects in self.items that have yet
        to have their ordered attribute be set to True """
        return [item for item in self.items if not item.has_been_ordered()]

    def total_cost(self):
        """ Function simply calculates the total cost of all the OrderItem
        objects currently in the self.items list attribute. """
        return sum((item.details.price for item in self.items))

class OrderItem:

    # Copied from lab 04 code.
    # Not sure if this will work right away. We'll see if it needs any changes.

    def __init__(self, menu_item):
        """ Constructor for the OrderItem class.
        Upon instantiation, sets the ordered attribute of the OrderItem object to False, and
        its status to REQUESTED. Also stores the <menu_item> MenuItem object (object that contains
        the information regarding the given OrderItem object) in the instance var self.details. """

        # Setting initial status of instantiated OrderItem to REQUESTED.
        # Refer to oorms.py/Notes 4 for an in depth explanation on status functionality.
        self.status = Status.REQUESTED;

        # Setting __ordered attribute and details of OrderItem
        self.__ordered = False
        self.details = menu_item


    # -------- Defining Methods --------

    def mark_as_ordered(self):
        """ Sets the self.ordered instance boolean var to true, and advances status from REQUESTED to PLACED.  """
        self.__ordered = True

        # Advancing status from REQUESTED to PLACED.
        self.advance_status();


    def has_been_ordered(self):
        """ Returns True if this OrderItem has been ordered and placed. Returns False otherwise. """
        return self.__ordered


    def has_been_served(self):
        """ I'm guessing we have this return True if this OrderItem object's current status is SERVED. """
        return self.status == Status.SERVED;


    def can_be_cancelled(self):
        """ Return true if current OrderItem can be cancelled - if status is REQUESTED or PLACED. False otherwise. """

        # Return true if current status' value is less than or equal to PLACED's value
        return int(self.status) <= int(Status.PLACED);


    def advance_status(self):
        """ Method advances current status of current item (PLACED --> COOKED --> READY --> SERVED). """

        # Knowing that int(self.status) returns the certain enumerated value to whatever constant self.status is
        # currently set to, and that Status(this_int) returns the enumerated constant in the Status() class which
        # has the value of this_int, we can use the two to elegantly advance the OrderItem's status. Pretty neat, eh.
        self.status = Status(int(self.status) + 1);


    def get_status(self):
        """ Method returns the current status of a given OrderItem. """
        return self.status;




class MenuItem:
    """ Objects of this class hold the information pertaining to each OrderItem set on the menu. """

    def __init__(self, name, price):
        """ Constructor of MenuItem class.

        Upon instantiation, sets the name of the MenuItem to <name> and the
        price of the menu item to <price>. """
        self.name = name
        self.price = price



""" given code for OrderItem Class


class OrderItem:

    # TODO: need to represent item state, not just 'ordered', all methods will need modifying
    def __init__(self, menu_item):
        self.details = menu_item
        self.ordered = False

    def mark_as_ordered(self):
        self.ordered = True

    def has_been_ordered(self):
        return self.ordered

    def has_been_served(self):
        # TODO: correct implementation based on item state
        return False

    def can_be_cancelled(self):
        # TODO: correct implementation based on item state
        return True

"""