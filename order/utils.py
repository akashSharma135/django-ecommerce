import datetime

def generate_order_number(data) -> str:
    """ generates an unique order id """
    yr = int(datetime.date.today().strftime('%Y'))
    dt = int(datetime.date.today().strftime('%d'))
    mt = int(datetime.date.today().strftime('%m'))
    d = datetime.date(year=yr, month=mt, day=dt)
    current_date = d.strftime('%Y%m%d')
    order_number = current_date + str(data.id)
    return order_number