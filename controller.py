"""

    Description:

    Provides the controller layer for the OORMS system.

    Notes:
        - None for now


    Submitting lab group: OCdt Al-Ansar Mohammed, OCdt Velasco
    Submission date: November 24th, 2022

    Original code by EEE320 instructors.

"""

# Is this the right spot for this?
from model import BillStatus; # <-- May end up removing if move applicable code to model.py


class Controller:

    def __init__(self, view, restaurant):
        """ Constructor of Controller object.

        <view> is a RestaurantView object that handles all the drawing of the user interfaces of its child classes,
        and <restaurant> is a Restaurant object which contains all the data used to draw out the tables, chairs,
        and orders. """

        self.view = view
        self.restaurant = restaurant


class RestaurantController(Controller):
    """ Controller for the restaurant view in the ServerView object. """

    def create_ui(self):
        """ Calling .create_ui() method from this class back in the ServerView object calls the create_restaurant_ui().
        Essentially calls the method to draw the entire restaurant into the canvas. """

        self.view.create_restaurant_ui()


    def table_touched(self, table_number):
        """ Sets the current controller of the ServerView object to the TableController
        associated with the table of <table_number>.  """
        self.view.set_controller(TableController(self.view, self.restaurant,  self.restaurant.tables[table_number]))
        self.view.update()



class TableController(Controller):
    """ Controller for the view of a given table within the restaurant in the ServerView object. """

    def __init__(self, view, restaurant, table):
        """ Constructor of TableController object.

        <view> is a ServerView object that handles all the drawing of the user interfaces, <restaurant>
        is the Restaurant object which contains all the data used to draw out the tables, chairs, and orders,
        <table> is a specific table object that was clicked on. """

        super().__init__(view, restaurant)
        self.table = table


    def create_ui(self):
        """ Calling .create_ui() method calls the create_table_ui() back in the user interface.
        Essentially draws the specific table and associated chairs of this TableController onto the canvas. """
        self.view.create_table_ui(self.table)

    def seat_touched(self, seat_number):
        """ Sets the current controller of the ServerView window to be the OrderController associated with the
        seat that just touched - opens up the order menu of the corresponding chair.  """
        self.view.set_controller(OrderController(self.view, self.restaurant, self.table, seat_number))
        self.view.update()

    def make_bills(self, printer):


        # Switching the payment controller of the bill pressed
        this_control = PaymentController(self.view, self.restaurant, self.table);
        self.view.set_controller(this_control);
        self.view.update();

        # Print shit in the printer
        printer.print(f'Set up bills for table {self.restaurant.tables.index(self.table)}')


    def done(self):
        """ Method returns the controller back to RestaurantController - setting the user interface back
        to the view of the restaurant. """
        self.view.set_controller(RestaurantController(self.view, self.restaurant))
        self.view.update()


class OrderController(Controller):

    def __init__(self, view, restaurant, table, seat_number):
        """ Constructor of OrderController object.

        <view> is a ServerView object that handles all the drawing of the user interfaces, <restaurant>
        is the Restaurant object which contains all the data used to draw out the tables, chairs, and orders,
        <table> is a specific table object that was clicked on, <seat_number> is the number of the seat at the table
        that was clicked on. """

        super().__init__(view, restaurant)
        self.table = table
        self.order = self.table.order_for(seat_number)


    def create_ui(self):
        """ Calling .create_ui() method calls the create_table_ui() back in the user interface.
        Essentially draws the order menu associated with the specific chair touched onto the canvas. """
        self.view.create_order_ui(self.order)

    def add_item(self, menu_item):
        """ Method that adds item to the "to be ordered" list when the order user interface is up.

        Function does this by adding the item through the Order object's .add_item() method, and
        updates the order user_interface by calling view.update().  """
        self.order.add_item(menu_item)
        self.restaurant.notify_views()

    def remove(self, order_item):
        """ Method removes passed in <order_item> from the table's order. """
        self.order.remove_item(order_item)
        self.restaurant.notify_views()

    def update_order(self):
        """ Method responsible for placing the requested orders into the PLACED status and set its __ordered attribute
        to True. Furthermore, placed orders show up in the KitchenView window, and ServerView returns to the table
        that was previously click on. """
        self.order.place_new_orders()
        self.view.set_controller(TableController(self.view, self.restaurant, self.table))
        self.restaurant.notify_views()

    def cancel_changes(self):
        """ Method is responsible for cancelling an order whose items have yet to be placed (still in REQUESTED status).

        Method is called when 'Cancel' button in order user interface is pressed. After pressing, returns ServerView
        to the table associated with the chair whose order was just cancelled. """
        self.order.remove_unordered_items()
        self.view.set_controller(TableController(self.view, self.restaurant, self.table))
        self.restaurant.notify_views()


class PaymentController(Controller):
    """ Handles events from the Payment UI. """


    def __init__(self, view, restaurant, table):
        """ Class constructor. """

        # Superclass constructor
        super().__init__(view, restaurant);

        # Saving the table passed in as an attribute
        self.table = table;


    def create_ui(self):
        """ Legit creates the payment ui of the table selected. """

        # Add a Bill Object to the table if there is none before.
        if len(self.table.return_bills()) == 0:
            self.table.add_bill();


        self.view.create_payment_ui(self.table);


    def bill_object_pressed(self, bill_obj):
        """ Handles the event when a bill object is pressed. Switches to bill controller to
        opens the bill object's UI. """

        this_controller = BillController(self.view, self.restaurant, self.table, bill_obj);
        self.view.set_controller(this_controller);
        self.view.update();


    def add_bill_pressed(self):
        """ Method adds a bill object of the associated table. Re-updates UI. """
        self.table.add_bill();
        self.create_ui();
        print("\nCurrent have", len(self.table.return_bills()), "bill objects with this table.");


    def exit_pressed(self):
        """ Handler that exits Payment UI back to table view. """


        # switching controller
        this_control = TableController(self.view, self.restaurant, self.table);
        self.view.set_controller(this_control);
        self.view.update()



class BillController(Controller):
    """ Handles events from the Bill UI. """

    def __init__(self, view, restaurant, table, this_bill):
        """ Constructor of the Bill Controller. """
        super().__init__(view, restaurant);

        # Saving the bill object and the associated table through attributes
        self.table = table; # I might not need this
        self.this_bill = this_bill;


    def create_ui(self):
        """ legit creates ui back in the view. """
        self.view.create_bill_ui(self.this_bill);

    def pay_bill(self):
        """ Method sets the current bill to paid status, and all of the added seats to paid status too. """

        # Can only pay off the bill if it has any added_orders in it. If not, print error message and stop function.
        if len(self.this_bill.added_orders) == 0:
            print("\nERROR: Can't pay off a bill if there are no added orders.");
            return;

        # Loop through bills added seat orders, advance their status to PAID. #todo move this in to the model.py?
        for this_order in self.this_bill.added_orders:
            this_order.advance_status();

        # Set this bill's status to paid
        self.this_bill.set_paid();

        # Re-update the UI
        self.create_ui();

    def delete_bill(self):
        """ Method deletes the current bill by first setting all of its added orders to UNASSIGNED, and
        then removing the bill from the list of the table's bills. """

        # Can only delete bill if it's status is not PAID. If it is, throw a print message error.
        # todo move into model? for weak coupling
        if self.this_bill.get_status() == BillStatus.PAID:
            print("\nERROR: Can not delete a paid bill lmao wut r u doing.");
            return;

        # Check if this is the last bill. If it is, it can't be deleted.
        if len(self.table.return_bills()) == 1:
            print("\nERROR: Can't delete all the bills. Must always have minimum of 1 at all times.");
            return;

        # Loop through the bill's added orders, and set unassigned
        for this_order in self.this_bill.added_orders:
            this_order.set_unassigned();

        # Switch the controller back to the Payment UI, and delete the bill
        self.this_bill.delete();
        self.exit_pressed();

        # Print statement
        print(self.table.return_bills());



    def add_order_pressed(self, seat_order_pressed):
        """ Method adds the unassigned seat whose button was pressed to the current bill object whose
        controller is currently set as the current one. Re-updates UI after adding.  """

        self.this_bill.add_order(seat_order_pressed)
        self.create_ui();

    def exit_pressed(self):
        """ Handler that exits Bill UI back to Payment UI. """

        # switching controller
        this_control = PaymentController(self.view, self.restaurant, self.table);
        self.view.set_controller(this_control);
        self.view.update()

