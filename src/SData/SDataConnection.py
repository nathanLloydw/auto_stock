import datetime
import requests
import time


class SdataConnection:

    def __init__(self,Auth_user,Auth_pass,base_url):
        self.authUser = Auth_user
        self.authPass = Auth_pass
        self.baseUrl = base_url

    def HTTP_Request(self,Url):
        """
        Method Name:
            HTTP_Request
        Summary:
            Web URLs are passed to this function for it to make the HTTPRequest,
            to sage and return the following data in json format.
        Input Parameters:
            Url(String) : this argument dictates the HTTPRequest and thus what is returned.
        Output Parameters:
            json_data(JSON) : the resulting json data it returned to where it was called to be decoded.
        """
        attempts = 0
        response_code = 0
        while attempts < 5:
            try:
                response = requests.get(Url, auth=(self.authUser, self.authPass))
                json_data = (response.json())
                response_code = response.status_code
                data = json_data['$resources']
                if response_code != 200:
                    print('------------------------------------------------ error --------------------------------------------------')
                    attempts = attempts + 1
                    time.sleep(attempts*(60*5))
                    data = self.HTTP_Request(Url)
                return data
            except:
                attempts = attempts + 1
                time.sleep(attempts*(60*5))
                print("waiting ...")
                print("waiting   ...")
                print("waiting     ...")
                print("waiting   ...")
                print("waiting ...")
        return 0

    def get_products(self):
        """
        Method Name:
            get_products
        Summary:
            Makes a HTTP Request to the sage server asking for x ammount of products,
            converts the products from JSON to an array in which it returns.

        Input Parameters:
            count(string or int): this argument specifies the amount of products the HTTP request will ask for.

        Output Parameters:
            products[] : an array of products.
        """

        Url = str(self.baseUrl)+"commodities?select=reference,name,salesPrice,freeStock,cost,OnOrder,weight&format=json"

        products = []

        json_products = self.HTTP_Request(Url)

        for product in json_products:
            uuid = product['$uuid']
            PrdID = product['reference']
            name = product['name']
            price = product['salesPrice']
            cost = product['cost']
            stock = product['freeStock']
            weight = product['weight']
            products.append((uuid,PrdID, name, price,cost, stock,weight))

        return products

    def get_product(self,id):
        """
        Method Name:
            get_product
        Summary:
            Makes a HTTP Request to the sage server asking for one product with the given id,
            converts the products from JSON to an array in which it returns.

        Input Parameters:
            count(string or int): this argument specifies the amount of products the HTTP request will ask for.

        Output Parameters:
            products[] : an array of products.
        """

        Url = str(self.baseUrl)+"commodities?select=reference,name,salesPrice,freeStock,cost&where=reference eq '"+id+"'&format=json"
        product = []
        json_products = self.HTTP_Request(Url)

        for product in json_products:
            PrdID = product['reference']
            name = product['name']
            price = product['salesPrice']
            cost = product['cost']
            stock = product['freeStock']
            product = (PrdID, name, price,cost,stock)

        return product

    def get_customers(self):
        """
        Method Name:
            get_customers
        Summary:
            Makes a HTTP Request to the sage server asking for x ammount of customers,
            converts the products from JSON to an array in which it returns.
        Input Parameters:
            count(string or int): this argument specifies the amount of customers the HTTP request will ask for.
        Output Parameters:
            customers[] : an array of customers.
        """

        Url = str(self.baseUrl) + "tradingAccountCustomer?include=postalAddresses,phones&format=json"

        customers = []
        json_customers = self.HTTP_Request(Url)

        for customer in json_customers:
            uuid = customer['$uuid']
            customerID = customer['reference']
            name = customer['name']
            staff = customer['analysis3']

            if not customer['phones']['$resources'][0]['text']:
                phone = ""
            else:
                phone = customer['phones']['$resources'][0]['text']

            if not customer['postalAddresses']['$resources'][0]['address1']:
                address1 = ""
            else:
                address1 = customer['postalAddresses']['$resources'][0]['address1']

            if not customer['postalAddresses']['$resources'][0]['address2']:
                address2 = ""
            else :
                address2 = " "+str(customer['postalAddresses']['$resources'][0]['address2'])

            if not customer['postalAddresses']['$resources'][0]['address3']:
                address3 = ""
            else :
                address3 = ", "+str(customer['postalAddresses']['$resources'][0]['address3'])

            if not customer['postalAddresses']['$resources'][0]['address4']:
                address4 = ""
            else:
                address4 = ", "+str(customer['postalAddresses']['$resources'][0]['address4'])

            townCity = customer['postalAddresses']['$resources'][0]['townCity']
            zipPostCode = customer['postalAddresses']['$resources'][0]['zipPostCode']

            address = str(address1)+str(address2)+str(address3)+str(address4)

            customers.append((uuid,customerID,name,phone,staff,address,townCity,zipPostCode))
        return customers

    def get_suppliers(self):
        """
        Method Name:
            get_suppliers
        Summary:
            Makes a HTTP Request to the sage server asking for x ammount of suppliers,
            converts the products from JSON to an array in which it returns.
        Input Parameters:
            count(string or int): this argument specifies the amount of suppliers the HTTP request will ask for.
        Output Parameters:
            suppliers[] : an array of suppliers.
        """

        Url = str(self.baseUrl)+"tradingAccountSupplier?select=reference,uuid,name,phones/*,emails/*,contacts/*&where=reference ne 'TEST'&format=json"

        suppliers = []
        json_suppliers = self.HTTP_Request(Url)

        for supplier in json_suppliers:
            uuid = supplier['$uuid']
            SlpID = supplier['reference']
            name = supplier['name']
            phones = supplier['phones']['$resources']
            telephone = phones[0]['text']
            contactType = phones[0]['type']
            emails = supplier['emails']['$resources']
            email1 = emails[0]['address']
            contact = supplier['contacts']['$resources']
            contactName = contact[0]['fullName']
            suppliers.append((uuid,SlpID, name, contactName, contactType, telephone, email1))
        return suppliers

    def get_orders_in_by_supplier(self,id):
        """
        Method Name:
            get_orders_in_by_supplier
        Summary:
            makes a HTTPRequest to Sage for orders which have been put in from a specific supplier,
            used to create Many To Many connection.
        Input Parameters:
            id(string): The unique identifier used on sage for a supplier.
        Output Parameters:
            orders[]: an array of orders.
        """
        id = id.replace("&", "%26")
        Url = str(self.baseUrl)+"purchaseOrders?where=SupplierId eq '"+str(id)+"'&select=reference,date,deliveryDate&orderBy=date desc&format=json"

        orders = []
        json_orders = self.HTTP_Request(Url)

        for order in json_orders:
            orderReference = order['reference']
            orderDate = order['date']
            dueDate = order['deliveryDate']

            orderDate = str(orderDate).split("(")
            dueDate = str(dueDate).split("(")

            orderDate = datetime.datetime.fromtimestamp(float(orderDate[1][0:10])).strftime('%Y-%m-%d')
            if len(dueDate) > 1:
                dueDate = datetime.datetime.fromtimestamp(float(dueDate[1][0:10])).strftime('%Y-%m-%d')
            else:
                dueDate = "on order"

            orderLines = self.get_order_in_details_by_id(orderReference)
            for orderLine in orderLines:
                orders.append((orderLine[0],orderLine[1]))
        return orders

    def get_order_in_details_by_id(self,OrderRef):
        """
        Method Name:
            get_order_in_details_by_id
        Summary:
            Once you have detils about an order this method is used,
             it get thr details of the products with in the order per line.
        Input Parameters:
            OrderRef(int): The unique identifier used on sage for a order.
        Output Parameters:
            orderLines[]: an array of the order/product details.
        """
        Url = str(self.baseUrl)+"purchaseOrderLines?where=reference eq "+str(OrderRef)+"&select=quantity,commodity/*&format=json"

        orderLines = []
        json_orderLines = self.HTTP_Request(Url)

        for orderLine in json_orderLines:
            products = orderLine['commodity']
            orderLines.append((products['reference'], products['cost'], orderLine['quantity']))

        return orderLines

    def get_active_orders_in(self):
        """
        Method Name:
            get_active_orders_in
        Summary:
            using the HTTPRequest method this function returns a list of active orders we are expecting to be delivered.
        Input Parameters:
            ref(int): to prevent over working sage we give it the last order we have to prevent it looking before that.
        Output Parameters:
            orders[]: an array of orders containg id, status, date, user, etc.
        """
        Url = str(self.baseUrl)+"purchaseOrders?orderBy=reference asc&select=reference,status,deliveryDate,date,user,SupplierId&where=(status eq 'On Order') or (status eq '' and statusFlagText eq '')&format=json"

        orders = []

        json_orders = self.HTTP_Request(Url)
        for order in json_orders:
            OrdID = order['reference']
            Status = order['status']

            dueDate = order['deliveryDate']
            if dueDate:
                dueDate = str(dueDate).split("(")
                dueDate = datetime.datetime.fromtimestamp(float(dueDate[1][0:10])).strftime('%Y-%m-%d')
            else:
                dueDate = 'n/a'

            orderDate = order['date']
            orderDate = str(orderDate).split("(")
            orderDate = datetime.datetime.fromtimestamp(float(orderDate[1][0:10])).strftime('%Y-%m-%d')

            user = order['user']
            supplierId = order['SupplierId']

            activeOrdersDetails = self.get_active_orders_in_details(OrdID)

            for ActiveOrder in activeOrdersDetails:
                id = ActiveOrder[0]
                quantity = ActiveOrder[1]
                orders.append((OrdID, Status, orderDate, dueDate, user, supplierId, id, quantity))

        return orders

    def get_orders_in_between_x_and_y(self,x):
        """
        Method Name:
            get_completed_orders_in
        Summary:
            gets a list of all completed orders since christmas (3 months at the time of use).
            used to fill the local Db.
        Input Parameters:
            None.
        Output Parameters:
             orders[]: an array of orders containg id, status, date, user, etc.
        """

        Url = str(self.baseUrl) + "purchaseOrders?where=reference between "+str(x)+" and "+str(x+1000)+"&format=json"

        orders = []

        json_orders = self.HTTP_Request(Url)
        for order in json_orders:
            OrdID = order['reference']
            Status = order['status']

            dueDate = order['deliveryDate']
            if dueDate:
                dueDate = str(dueDate).split("(")
                dueDate = datetime.datetime.fromtimestamp(float(dueDate[1][0:10])).strftime('%Y-%m-%d')
            else:
                dueDate = 'n/a'

            orderDate = order['date']
            orderDate = str(orderDate).split("(")
            orderDate = datetime.datetime.fromtimestamp(float(orderDate[1][0:10])).strftime('%Y-%m-%d')

            user = order['user']
            supplierId = order['SupplierId']

            activeOrdersDetails = self.get_active_orders_in_details(OrdID)

            for ActiveOrder in activeOrdersDetails:
                id = ActiveOrder[0]
                quantity = ActiveOrder[1]
                orders.append((OrdID, Status, orderDate, dueDate, user, supplierId, id, quantity))

        return orders

    def get_active_orders_in_details(self,OrdID):
        """
        Method Name:
            get_active_orders_in_details
        Summary:
            gets order details by given ID.
        Input Parameters:
            OrdID(int): The given ID, used in the HTTP request to select a specific order.
        Output Parameters:
        activeOrderDetails[]: an array of the orderReference/product details.
        """
        Url = str(self.baseUrl)+"purchaseOrderLines?select=quantity,commodity/*&where=reference eq "+str(OrdID)+"&format=json"

        activeOrderDetails = []

        json_products = self.HTTP_Request(Url)

        for product in json_products:

            if product['commodity']:
                productId = product['commodity']['reference']
            else:
                productId = 'n/a'

            productQuantity = product['quantity']
            activeOrderDetails.append((productId,productQuantity))

        return activeOrderDetails

    def get_order_in_status(self,ref):
        """
        Method Name:
            get_order_in_status
        Summary:
            used to check all our pending orders to see if they have arrived.
        Input Parameters:
            ref(int): order reference
        Output Parameters:
            status(int): determines the status of the order
        """
        Url = str(self.baseUrl) + "purchaseOrders?select=status,statusFlagText&where=reference eq " + str(ref) + "&format=json"

        status = 0

        json_orders = self.HTTP_Request(Url)

        for order in json_orders:
            Status01 = order['status']
            Status02 = order['statusFlagText']

            if Status01 == "On Order":
                status = 1
            elif Status02 == "Complete":
                status = 2
            elif Status01 == "Cancelled":
                status = 3

        return status

    def get_invoice_between_x_and_y(self,refx,refy):
        """
            Method Name:
                get_invoice_between_x_and_y
            Summary:
                returns all invoives between reference x and y.
            Input Parameters:
                refx(int): determines what reference we are starting the search from.
                refy(int): determines the reference we stop the search.
            Output Parameters:
                products_details[]: product infomation regarding the invoice number.
            """

        if refx == refy:
            return 0

        Url = str(self.baseUrl) + "salesInvoiceLines?select=reference,quantity,actualPrice,commodity/*&where=reference between "+str(refx)+" and "+str(refy)+"&format=json"

        products_details = []

        json_products_details = self.HTTP_Request(Url)

        details = []
        ref = 0

        for product in json_products_details:
            reference = product['reference']
            id = product['commodity']['reference']
            quantity = product['quantity']
            cost = product['actualPrice']

            if ref != reference:
                ref = reference
                details = self.get_order_details(ref, quantity)[0]

            date = details[0]
            customer = details[1]
            user = details[2]

            products_details.append([reference, id, quantity, cost, date, customer, user])

        return products_details

    def get_newest_invoices(self,ref, count):
        """
        Method Name:
            get_newest_invoices
        Summary:
            returns all invoives newer than the last invoice we checked.
        Input Parameters:
            ref(int): determines what reference we are starting the search from.
            count(int): determines how many invoices ahead we are grabbing.
        Output Parameters:
            products_details[]: product infomation regarding the invoice number.
        """
        Url = str(self.baseUrl)+"salesInvoiceLines?select=reference,quantity,actualPrice,commodity/*&where=reference between "+str(ref)+" and "+str(int(ref)+count)+"&format=json"

        products_details = []

        json_products_details = self.HTTP_Request(Url)

        details = []
        ref = 0

        for product in json_products_details:
            reference = product['reference']
            id = product['commodity']['reference']
            quantity = product['quantity']
            cost = product['actualPrice']

            if ref != reference:
                ref = reference
                details = self.get_order_details(ref, quantity)[0]

            date = details[0]
            customer = details[1]
            user = details[2]

            products_details.append([reference, id, quantity, cost,date,customer,user])

        return products_details

    def get_order_details(self,ref,quantity):
        if quantity > 0:

            details = self.get_invoice_details(ref)
        else:
            details = self.get_credit_details(ref)

        if details:
            date = details[0][0]
            customer = details[0][1]
            user = details[0][2]
        else:
            date = datetime.datetime.now()
            customer = 'n/a'
            user = 'n/a'
        details.append([date,customer,user])
        return details

    def get_invoice_details(self,ref):
        """
        Method Name:
            get_order_details
        Summary:
            gets invoice details for a specific reference.
        Input Parameters:
            ref(int): reference to specific order we are looking for.
        Output Parameters:
            details[]: details such as date, customer and user for order.
        """
        Url = str(self.baseUrl) + "salesInvoices?select=date,CustomerId,user&where=reference eq " + str(ref) + "&format=json"
        details = []

        json_date_details = self.HTTP_Request(Url)

        for invoice in json_date_details:
            orderDate = invoice['date']
            customer = invoice['CustomerId']
            user = invoice['user']
            orderDate = str(orderDate).split("(")
            orderDate = datetime.datetime.fromtimestamp(float(orderDate[1][0:10])).strftime('%Y-%m-%d')
            details.append([orderDate, customer, user])

        return details

    def get_credit_details(self,ref):
        """
        Method Name:
            get_credit_details
        Summary:
            gets credit details for a specific reference.
        Input Parameters:
            ref(int): reference to specific credit we are looking for.
        Output Parameters:
            details[]: details such as date, customer and user for credit.
        """
        Url = str(self.baseUrl) + "salesCredits?select=date,CustomerId,user&where=reference eq " + str(ref) + "&format=json"
        details = []

        json_date_details = self.HTTP_Request(Url)

        for invoice in json_date_details:
            orderDate = invoice['date']
            customer = invoice['CustomerId']
            user = invoice['user']
            orderDate = str(orderDate).split("(")
            orderDate = datetime.datetime.fromtimestamp(float(orderDate[1][0:10])).strftime('%Y-%m-%d')
            details.append([orderDate, customer, user])

        return details

    def get_invoice_by_id(self,ref):
        """
        Method Name:
            get_invoice_by_id
        Summary:
            returns an invoice from sage which matches the given reference.
        Input Parameters:
            ref(int): the order reference which we are looking for from sage.
        Output Parameters:
            product_details[]: the details about the order & products such as product id,
                               quantity and price.
        """
        Url = str(self.baseUrl) + "salesInvoiceLines?select=reference,quantity,actualPrice,commodity/*&where=reference eq " + str(ref) + "&format=json"

        products_details = []

        json_products_details = self.HTTP_Request(Url)

        for product in json_products_details:
            reference = product['reference']
            id = product['commodity']['reference']
            quantity = product['quantity']
            cost = product['actualPrice']
            products_details.append([reference, id, quantity, cost])
        return products_details
