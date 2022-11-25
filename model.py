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
    item when placed within the ServerView window. """

    REQUESTED = -1;
    PLACED = 0;
    SERVED = 1;


class SeatOrderStatus(enum.IntEnum):
    """ Enumerated constants of type enum.IntEnum with linear values that track the state of a given seat
    order within the Payment UI and whether if it has no items added to it, if it is unassigned, assigned to a bill,
    or been paid off. """

    NO_ITEMS = -1;
    UNASSIGNED = 0;
    ASSIGNED = 1;
    PAID = 2;

    
class BillStatus(enum.IntEnum):
    """ Enumerated constants of type enum.IntEnum to track whether a given bill object has been paid or has
    yet to be paid."""
    
    NOT_PAID = 0;
    PAID = 1;



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

        # Create a list of all the bill objects made with the table, and
        # and a counter to keep track of number of added bills (will be used as the bill's ID)
        self._bills = [];
        self.bill_ID_counter = 0;


    def add_bill(self):
        """ Method adds a Bill Object to this Table object. Incrementing self.bill_counter whenever a bill is made.
        Can only create as many bills objects as there are seats who have made orders at the table.

        Method also returns the added bill. """

        # Getting number of active orders of table
        order_count = 0;
        for this_order in self.orders:
            if len(this_order.get_items()) > 0:
                order_count += 1;

        # If more bills than allowed is being added, throw error. Otherwise, add a bill object
        # with the current bill count as its ID.
        if len(self._bills) < order_count:
            self._bills.append(Bill(self, self.bill_ID_counter));
            self.bill_ID_counter += 1;
        else:
            print("\nERROR: Can only add as many bills as there are seats who've made orders.");


    def remove_bill(self, to_remove):
        """ Method removes a bill in the self._bills list.

        --> The bill to remove will always be in the list <-- """
        self._bills.remove(to_remove);

    def return_bills(self):
        """ Returns the list of bill objects made with this table. """
        return self._bills;

    def create_bill_for_each(self):
        """ Method creates a bill for each unassigned seat of the table,
        adds the unassigned seats to their respective bills. """

        # Delete all the UNASSIGNED and ASSIGNED bills already made with the table first
        for i in range(len(self._bills) - 1, -1, -1):
            self._bills[i].delete();

        # For each unassigned order...
        for this_seat_order in self.return_unassigned_orders():

            # Create new bill object
            new_bill = Bill(self, self.bill_ID_counter);
            self.bill_ID_counter += 1; # Increment obviously

            # Add the order to the bill
            new_bill.add_order(this_seat_order);

            # Add the bill to the bill list of the table
            self._bills.append(new_bill);


    def all_one_bill(self):
        """ Method creates one bill object to add all the seat orders with order items
        in them to said bill. """

        # Delete all the UNASSIGNED and ASSIGNED bills already made with the table first
        counter = 0;
        for i in range(len(self._bills) - 1, -1, -1):
            if self._bills[i].delete():
                counter += 1;
        print(f"\n{counter} NUMBER OF BILLS DELETED.")

        # Create a new bill, and add all the seat orders
        new_bill = Bill(self, self.bill_ID_counter);
        for this_seat_order in self.return_unassigned_orders():
            new_bill.add_order(this_seat_order);

        # Add the bill object to the list of bills
        self._bills.append(new_bill);


    def has_any_active_orders(self):
        """ Returns True if there are still active orders pending that have not been served.
        If there are none, then obviously returns false. """
        for order in self.orders:
            for item in order.get_items():
                if item.has_been_ordered() and not item.has_been_served():
                    return True
        return False


    def has_order_for(self, seat):
        """ Function returns a boolean that indicates whether the given seat of number <seat> has ordered yet. """
        return bool(self.orders[seat].get_items())


    def order_for(self, seat):
        """ Function returns the specific Order object associated with the seat whose
        number <seat> has been passed through the arguments. """
        return self.orders[seat]


    def return_orders(self):
        """ Returns the list of all the orders placed (and not placed) with the table. """
        return self.orders;


    def return_unassigned_orders(self):
        """ Returns a list of all the orders that are unassigned. """
        return [this_order for this_order in self.orders if this_order.get_status() == SeatOrderStatus.UNASSIGNED];





class Order:

    def __init__(self, seat_number):
        """ Constructor for Order object.

        This object is responsible for keeping track of the orders placed by a given
        seat in the restaurant.

        Every seat at a table gets their own Order object created for it.

        <seat_number : int> : The number of seat which this Order object is associated with. """

        self.__items = []

        # Adding a seat number attribute to the order to track which seat made the order
        self.__seat_number = seat_number;

        # Defaulting the created Order's status to NO_ITEMS status.
        self.__status = SeatOrderStatus.NO_ITEMS;


    def advance_status(self):
        """ Method advances current status of current seat order (UNASSIGNED --> ASSIGNED --> PAID). """
        if int(self.__status) < int(SeatOrderStatus.PAID):
            prev_status = self.__status;
            self.__status = SeatOrderStatus(int(self.__status) + 1);
            print(f"\nCurrent __status of bill switched from {prev_status} to {self.__status}. ");


    def set_unassigned(self):
        """ Method sets the status of the this order object to UNASSIGNED.
        This method is used when a Bill object is being deleted. """
        self.__status = SeatOrderStatus.UNASSIGNED;


    def get_status(self):
        """ Method returns current status of given seat order. """
        return self.__status;


    def get_seat_number(self):
        """ Returns seat number associated of this Order object. """
        return self.__seat_number;


    def add_item(self, menu_item):
        """ Function adds the OrderItem object <menu_item> passed through
        the arguments into the self.items list attribute of the Order object.
        If it's the first item added, advance status from NO_ITEM to UNASSIGNED. """

        # If this is first item being added to Order, set Order status to UNASSIGNED
        if len(self.__items) == 0:
            self.advance_status();

        item = OrderItem(menu_item)
        self.__items.append(item)


    def remove_item(self, order_item):
        """ Function removes the <item> object passed through args from the self.items list"""
        self.__items.remove(order_item)


    def get_items(self):
        """ Method returns the list of OrderItem objects added to this order. """
        return self.__items;


    def place_new_orders(self):
        """ Function goes through the list attribute self.items of the given Order object and
        sets all OrderItem objects in the list's ordered attribute from False to True. """
        for item in self.unordered_items():
            item.mark_as_ordered()


    def remove_unordered_items(self):
        """ Function removes all the items in the list attribute self.items that have an "unordered" status. """
        for item in self.unordered_items():
            self.__items.remove(item)


    def unordered_items(self):
        """ Function returns a list of all OrderItem objects in self.items that have yet
        to have their ordered attribute be set to True """
        return [item for item in self.__items if not item.has_been_ordered()]


    def total_cost(self):
        """ Function calculates the total cost of all the OrderItem
        objects currently in the self.items list attribute. """
        return sum((item.details.price for item in self.__items))



class OrderItem:

    def __init__(self, menu_item):
        """ Constructor for the OrderItem class.
        Upon instantiation, sets the ordered attribute of the OrderItem object to False, and
        its status to REQUESTED. Also stores the <menu_item> MenuItem object (object that contains
        the information regarding the given OrderItem object) in the instance var self.details. """

        # Setting initial status of instantiated OrderItem to REQUESTED.
        self.__status = OrderStatus.REQUESTED;

        # Setting __ordered attribute and details of OrderItem.
        # (This is not needed so much in this lab)
        self.__ordered = False
        self.details = menu_item


    # -------- Defining Methods --------

    def mark_as_ordered(self):
        """ Sets the self.ordered instance boolean var to true, and advances status from REQUESTED to PLACED.  """
        self.__ordered = True
        self.advance_status();


    def has_been_ordered(self):
        """ Returns True if this OrderItem has been ordered and placed. Returns False otherwise. """
        return self.__ordered


    def has_been_served(self):
        """ I'm guessing we have this return True if this OrderItem object's current status is SERVED. """
        return self.__status == OrderStatus.SERVED;


    def can_be_cancelled(self):
        """ Return true if current OrderItem can be cancelled - if status is REQUESTED or PLACED. False otherwise. """

        # Return true if current status' value is less than or equal to PLACED's value
        return int(self.__status) <= int(OrderStatus.PLACED);


    def advance_status(self):
        """ Method advances current status of current item (PLACED --> COOKED --> SERVED). """
        self.__status = OrderStatus(int(self.__status) + 1);


    def get_status(self):
        """ Method returns the current status of a given OrderItem. """
        return self.__status;



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

    def __init__(self, table, ID):
        """ Constructor of the Bill object class.

        <table : Table> : This is the Table object the bill is created under.
        <ID : int> : Will serve as the number that be used in the Bill's label. """

        # Save table as attribute
        self.table = table;

        # Get the table's current seat orders
        self.table_orders = table.return_orders();

        # Create a list to store the added orders of this bill
        self.added_orders = [];

        # Initialize bill's status to be NOT_PAID upon creation.
        self.__status = BillStatus.NOT_PAID;

        # Saving the Bill's ID.
        self.ID = ID;


    def __del__(self):
        """ Method removes this bill object from its Table object's list of bills. """
        self.table.remove_bill(self);


    def get_status(self):
        """ Method returns current status of bill. """
        return self.__status;


    def set_paid(self):
        """ Sets the bill status to be SeatStatus.PAID.

        Will throw error message if Bill object has no added seat orders to it, or is already in PAID status."""

        # If no orders were added to bill, throw error.
        if len(self.added_orders) == 0:
            print("\nERROR: Can't pay off a bill if there are no added orders.");
            return;

        # Throw error  if user if the bill's status is already PAID.
        if self.__status == BillStatus.PAID:
            print("\nERROR: This bill has already been paid.");
            return;

        # Otherwise, Loop through the bills added seat orders and advance their status to PAID
        for this_order in self.added_orders:
            this_order.advance_status();

        # Set bill's status to PAID.
        self.__status = BillStatus.PAID;


    def is_paid(self):
        """ Method returns True if the current status of the bill is BillStatus.PAID. """
        return self.__status == BillStatus.PAID;


    def add_order(self, this_seat_order):
        """ Method adds a seat order at the table to this bill object. Only possible when __status is unpaid.

        <this_seat_order : Order> : The Order object that the user intends to add to this bill. """
        
        # Add to order only if it's __status is UNASSIGNED
        if this_seat_order.get_status() == SeatOrderStatus.UNASSIGNED:

            # Advance status of the order object to ASSIGNED
            this_seat_order.advance_status();

            self.added_orders.append(this_seat_order);

        else:
            print(f"\nCannot add order {this_seat_order.details.name} "
                  f"to order since is of __status {this_seat_order.__status}.")
    
    
    def delete(self):
        """ Method deletes this bill object if is not paid off. Sets all the added orders to unassigned __status.

         If bill object is already PAID off, throws an error and stops method.

         Returns True if bill object was successfully deleted. False otherwise. """

        # If bill is already paid, throw error message and stop method.
        if self.__status == BillStatus.PAID:
            print("\nERROR: Can not delete a paid bill. ");
            return False;

        # Loop through the bill's added orders and set them to UNASSIGNED status
        for this_order in self.added_orders:
            this_order.set_unassigned();

        # Remove the bill object from the associated table, and return True
        self.__del__();
        return True;






