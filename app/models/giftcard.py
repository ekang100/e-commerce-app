from flask import current_app as app

class GiftCard:
    def __init__(self, cardid, code, amount, redeem):
        self.cardid = cardid
        self.code = code
        self.amount = amount
        self.redeem = redeem
    
    #set redeem status to false when card used
    def redeem_card(code):
        try:
            app.db.execute("""
                UPDATE GiftCard
                SET redeem = TRUE
                WHERE code = :code
            """, code=code)
            return GiftCard.get_amount(code)
        except Exception as e:
            print(str(e))
            return None
    
    #get amount from a giftcard code
    @staticmethod
    def get_amount(code):
        rows = app.db.execute('''
SELECT amount
FROM GiftCard
WHERE code = :code
''',
                              code=code)
        return ((rows[0])[0]) if rows else None
    
    #get redeem status from a giftcard code
    @staticmethod
    def status(code):
        rows = app.db.execute('''
SELECT redeem
FROM GiftCard
WHERE code = :code
''',
                              code=code)
        # return GiftCard(*(rows[0])) if rows else None
        return ((rows[0])[0]) if rows else None
