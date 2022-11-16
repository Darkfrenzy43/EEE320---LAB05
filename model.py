"""

    Description:

    Provides the model classes representing the state of the OORMS
    system.

    Notes:
        - None for now


    Status:
        - beginning implementation of bill object

    Submitting lab group: OCdt Al-Ansar Mohammed, OCdt Velasco
    Submission date: November 24th, 2022

    Original code by EEE320 instructors.

"""

# ---- Importing built-in Libraries ----
import enum

# ---- Importing from other modules -----

from constants import TABLES, MENU_ITEMS


# ------ Defining Enumerated Constants ------

class OrderStatus(enum.IntEnum):
    """ Enumerated constants of type enum.IntEnum with linear values that track the state of a given order
    item when placed within the KitchenView window. """

    REQUESTED = -1; # damn, there ain't no elegant way to write this out xD
    PLACED = 0;
    COOKED = 1;
    READY = 2;
    SERVED = 3;

class PaymentStatus(enum.IntEnum):
    """ Enumerated constants of type enu.intenum with linear values that track the state of a given seat
    order within the Payment UI and whether if it's been unassigned to a bill, assigned, or been paid off. """

    UNASSIGNED = 0;
    ASSIGNED = 1;
    PAID = 2;
    
    REMOVED = 3;



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
        self.orders = [Order(seat_number) for seat_number in range(seats)]


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



    # Added method
    def return_orders(self):
        """ Returns the list of all the orders placed (and not placed) with the table. """
        return self.orders;


class Order:

    def __init__(self, seat_number):        # <--- Added new argument
        """ Constructor for Order object.

        In short, this object is responsible for keeping track of the orders placed by a given
        seat in the restaurant.

        Every chair gets their own Order object associated with it. """

        self.items = []

        # Adding a seat number attribute to the order to track which seat made the order
        self.__seat_number = seat_number;

        # Adding a status to the seat's order for the payment UI. Default to unassigned.
        self.__status = PaymentStatus.UNASSIGNED;



    def advance_status(self):
        """ Method advances current status of current seat order (UNASSIGNED --> ASSIGNED --> PAID). """
        self.__status = PaymentStatus(int(self.__status) + 1);

    def get_status(self):
        """ Method returns current status of given seat order. """
        return self.__status;

    def get_seat_number(self):
        """ Returns seat number associated of this Order object. """
        return self.__seat_number;


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
        self.status = OrderStatus.REQUESTED;

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
        return self.status == OrderStatus.SERVED;


    def can_be_cancelled(self):
        """ Return true if current OrderItem can be cancelled - if status is REQUESTED or PLACED. False otherwise. """

        # Return true if current status' value is less than or equal to PLACED's value
        return int(self.status) <= int(OrderStatus.PLACED);


    def advance_status(self):
        """ Method advances current status of current item (PLACED --> COOKED --> READY --> SERVED). """

        # Knowing that int(self.status) returns the certain enumerated value to whatever constant self.status is
        # currently set to, and that Status(this_int) returns the enumerated constant in the Status() class which
        # has the value of this_int, we can use the two to elegantly advance the OrderItem's status. Pretty neat, eh.
        self.status = OrderStatus(int(self.status) + 1);


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



# -------- Added Code ---------

class Bill:

    # Okay, we need the bill object to have access to the seats of the table, and in truth the table itself

    def __init__(self, table):

        # Save table as attribute
        self.table = table;

        # Get the seat orders and their statuses for the "right window" of the UI
        self.table_orders = table.return_orders();

        # Create an array of orders added to this bill
        self.added_orders = [];

        # Intialize status to unassigned. 
        self.__status = PaymentStatus.UNASSIGNED;

    def set_assigned(self):
        """ Method sets __status of bill object to ASSIGNED, only if current __status is UNASSIGNED. """
        if self.__status is PaymentStatus.UNASSIGNED:
            self.__status = PaymentStatus.ASSIGNED;
        else: 
            print(f"\nCurrent __status of bill can't be switched from {self.__status} to ASSIGNED.");


    def set_paid(self):
        """ Method sets __status of bill object to ASSIGNED, only if current __status is UNASSIGNED. """
        if self.__status is PaymentStatus.ASSIGNED:
            self.__status = PaymentStatus.PAID;
        else: 
            print(f"\nCurrent __status of bill can't be switched from {self.__status} to PAID. ");


    def add_order(self, this_seat_order):
        """ Method adds a seat order at the table to this bill object. Only possible when __status is unpaid.  """
        
        # Add to order only if it's __status is UNASSIGNED
        if this_seat_order.__status == PaymentStatus.UNASSIGNED:
            # todo - sort this in terms of seat number?
            self.added_orders.append(this_seat_order);
        else:
            print(f"\nCannot add order {this_seat_order.details.name} "
                  f"to order since is off __status {this_seat_order.__status}.")
    
    
    def delete(self):
        """ Method deletes this bill object if is not paid off. Sets all the added orders to unassigned __status. """
        for this_order in self.added_orders:
            this_order.__status = PaymentStatus.UNASSIGNED
    
        # Do removal from view somewhere here...
        self.__status = PaymentStatus.REMOVED;

        # todo - figure out how to destroy the object from the program.
    



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