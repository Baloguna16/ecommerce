from support.models import Product, Pick

def validate_ipn(ipn, backend):
    is_valid_transaction = False
    if ipn['payment_status'] == 'Completed': #check if ipn payment_status is 'Completed'
        if ipn['txn_id'] != backend['txn_id']: #check txn_id to make sure the transaction isnt duplicate
            if ipn['receiver_email'] == backend['receiver_email']:
                if ipn['mc_gross'] == backend['mc_gross']:
                    if ipn['mc_currency'] == backend['mc_currency']:
                        is_valid_transaction = True
    return is_valid_transaction

def paypalify(cart):
    transaction = [
        {"amount" : None},
        {"item_list" : None},
        {"description" : None}
        ]
    amount = {
        "total": None,
        "currency": "USD"
        }
    item_list = {"items" : []}
    item = {
        "name": None,
        "sku": None,
        "price": None,
        "currency": "USD",
        "quantity": None
        }
    description = None
    for product in cart.contents:
        count = Pick.query.filter_by(shopper_id=cart.owner_id).filter_by(product_id=product.id).first().count

        item["name"] = product.name
        item["sku"] = str(product.id)
        item["price"] = "{:,.2f}".format(product.price)
        item["quantity"] = str(count)

        item_list["items"].append(item)

    amount["total"] = "{:,.2f}".format(cart.total_cost)
    description = "First commit!"

    transaction[0]["amount"] = amount
    transaction[1]["item_list"] = item_list
    transaction[2]["description"] = description
    print(transaction)
    return transaction
