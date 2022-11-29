"""

    Description:

    Provides the controller layer for the OORMS system.

    Notes:
        - None for now


    Submitting lab group: OCdt Al-Ansar Mohammed, OCdt Velasco
    Submission date: November 24th, 2022

    Original code by EEE320 instructors.

"""


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
        """ Calling .create_ui() method calls the create_table_ui() back in the view.
        Essentially draws the specific table and associated chairs of this TableController onto the canvas. """
        self.view.create_table_ui(self.table)


    def seat_touched(self, seat_number):
        """ Sets the current controller of the ServerView window to be the OrderController associated with the
        seat that just touched - opens up the order menu of the corresponding chair.  """
        self.view.set_controller(OrderController(self.view, self.restaurant, self.table, seat_number))
        self.view.update()


    def make_bills(self, printer):
        """ Method is run when the "Create Bills" button is pressed from a given table's UI.
        Method sets current controller of the ServerView Window to be the PaymentController associated with the table
        that is to have their bills created. """
        this_control = PaymentController(self.view, self.restaurant, self.table, printer);
        self.view.set_controller(this_control);
        self.view.update();


    def done(self):
        """ Method returns the controller back to RestaurantController - setting the user interface back
        to the view of the restaurant. """
        self.view.set_controller(RestaurantController(self.view, self.restaurant))
        self.view.update()



class OrderController(Controller):

    def __init__(self, view, restaurant, table, seat_number):
        """ Constructor of OrderController object.

        <view> is a RestaurantView object that handles all the drawing of the user interfaces, <restaurant>
        is the Restaurant object which contains all the data used to draw out the tables, chairs, and orders,
        <table> is a specific table object that was clicked on, <seat_number> is the number of the seat at the table
        that was clicked on. """

        super().__init__(view, restaurant)
        self.table = table
        self.order = self.table.order_for(seat_number)


    def create_ui(self):
        """ Calling .create_ui() method calls the create_table_ui() back in the view.
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

    def __init__(self, view, restaurant, table, printer):
        """ Class constructor.

        <view : RestaurantView> : The window where the Payment UI is to be drawn.
        <restaurant : Restaurant> : The restaurant object which contains all the model info of the tables, chairs,
            orders, etc.
        <table : Table> : The specific table object whose bills are to be created.
        <printer : Printer> : The printer object where the bills are to be printed on. """

        # Calling super constructor and saving the attributes.
        super().__init__(view, restaurant);
        self.table = table;
        self.printer = printer


    def create_ui(self):
        """ Calling .create_ui() method calls the create_payment_ui() back in the view, which
        draws out the payment UI of the selected table. """

        self.view.create_payment_ui(self.table);


    def bill_object_pressed(self, bill_obj):
        """ Is called when a Bill Object's button in the UI is pressed. Switches view's current controller to
        that of the pressed Bill Object.  """
        this_controller = BillController(self.view, self.restaurant, self.table, bill_obj, self.printer);
        self.view.set_controller(this_controller);
        self.view.update();


    def add_bill_pressed(self):
        """ This method is called when the "Add Bill" button is pressed.
        Method adds a new bill object to the table, and re-updates UI. """
        self.table.add_bill();
        self.create_ui();


    def exit_pressed(self):
        """ This method is called when "EXIT" button in the UI is pressed. Switches controller back to 
        the TableController of the selected Table object. """
        this_control = TableController(self.view, self.restaurant, self.table);
        self.view.set_controller(this_control);
        self.view.update()

    def each_own_bill_pressed(self):
        """ Method creates a bill for each seat with orders in it status in the UI, and adds those seats. """

        # Calling the appropriate method of the table object, and re-drawing UI.
        self.table.create_bill_for_each();
        self.create_ui();

    def all_one_bill_pressed(self):
        """ Method creates one bill and adds all the seats of the """

        # Calling appropriate method and re-draw UI
        self.table.all_one_bill();
        self.create_ui();

    def print_paid_bills_pressed(self):
        """ Method is called when "Print and Pay Bills" button is pressed.
        Method attempts to print all the bills currently in UI and sets them to all paid status. """

        # Calling appropriate method and re-draw UI
        if self.table.set_all_paid():
            self.printer.print_paid_bills(self.table.return_paid_bills());
            self.create_ui();
        else:
            self.printer.print_error();



class BillController(Controller):
    """ Handles events from the Bill UI. """

    def __init__(self, view, restaurant, table, bill, printer):
        """ Constructor of the Bill Controller. 
        
        <view : RestaurantView> : The window where the Bill UI is to be drawn.
        <restaurant : Restaurant> : The restaurant object which contains all the model info of the tables, chairs,
            orders, etc.
        <table : Table> : The specific table object whose bills are to be created.
        <bill : Bill> : The specific bill object whose UI is being drawn.
        <printer : Printer> : The printer object where the bills are to be printed on.
        """

        # Calling super constructor and saving the passed in objects as attributes
        super().__init__(view, restaurant);
        self.table = table;
        self.bill = bill;
        self.printer = printer;


    def create_ui(self):
        """ Calling .create_ui() method calls the create_bill_ui() back in the view, which
        draws out the bill UI of the selected Bill object. """
        self.view.create_bill_ui(self.bill);


    # oh lol. Guess this method never got used.
    def pay_bill(self):
        """ Method attempts sets the current bill and all the added seat orders to paid status.
        Will throw error message if Bill object has no added seat orders to it, or is already in PAID status. """

        # Attempt to set Bill status to PAID. Method
        # below will throw error if conditions are not met.
        self.bill.set_paid();

        # Re-update the UI, even if bill failed to be set to PAID.
        self.create_ui();


    def delete_bill(self):
        """ Method attempts to delete the current bill.

         First, sets all the added seat orders to UNASSIGNED status, then removes bill from the list of
         the associated Table object's bills. If successful in deletion, returns to Payment UI.

         If bill object is already PAID off, throws an error and stops method. """

        # Attempt to delete bill. If successful, exit the Bill UI.
        if self.bill.delete():
            self.exit_pressed();


    def add_order_pressed(self, seat_order_pressed):
        """ Method adds the unassigned seat whose plus button was pressed to the current bill object.
        Re-updates UI accordingly.

        <seat_order_pressed : Order> : The Order object of the seat who is trying to be added to the current
        Bill Object. """

        self.bill.add_order(seat_order_pressed)
        self.create_ui();


    def exit_pressed(self):
        """ Handler is called when 'EXIT' button is pressed in the Bill UI. Switches current controller to the
        PaymentController associated with the Bill object. """
        this_control = PaymentController(self.view, self.restaurant, self.table, self.printer);
        self.view.set_controller(this_control);
        self.view.update()


# Cleaned and good to go for now.
