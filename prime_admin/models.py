from threading import local
import pytz
from config import TIMEZONE
from datetime import datetime
from enum import unique
from mongoengine.fields import DateField, EmbeddedDocumentListField
from app import db
from app.admin.models import Admin
from app.core.models import Base
from bson.objectid import ObjectId
from prime_admin.utils.date import format_utc_to_local
from prime_admin.utils.currency import convert_decimal128_to_decimal, format_to_str_php



class Payment(db.EmbeddedDocument):
    # custom_id = db.StringField(primary_key=True)
    _id = db.ObjectIdField( required=True, default=lambda: ObjectId())
    deposited = db.StringField()
    payment_mode = db.StringField()
    amount = db.DecimalField()
    current_balance = db.DecimalField()
    confirm_by = db.ReferenceField('User')
    date = db.DateTimeField()
    payment_by = db.ReferenceField('Registration')
    earnings = db.DecimalField()
    savings = db.DecimalField()
    status = db.StringField()
    branch = db.ReferenceField('Branch')
    created_at = db.DateTimeField()
    contact_person = db.ReferenceField('User')
    thru = db.StringField()
    reference_no = db.StringField()
    receipt_path = db.StringField()
    payment_method = db.StringField()
    is_expenses = db.BooleanField(default=False)

    @property
    def id(self):
        if not self._id:
            return ''

        return str(self._id)


class Student(object):
    def __init__(self, document, branch=None, batch_no=None):
        self.data = document
        self.__dict__.update(document)

        self.branch = branch if branch else None
        self.batch_no = batch_no if batch_no else None

    def get_amount(self, currency=False):
        if currency:
            return format_to_str_php(self.data.get('amount'))
        return convert_decimal128_to_decimal(self.data.get('amount'))

    def get_amount_deposit(self):
        return convert_decimal128_to_decimal(self.data.get('amount_deposit'))

    def get_balance(self, currency=False):
        if currency:
            return format_to_str_php(self.data.get('balance'))
        return convert_decimal128_to_decimal(self.data.get('balance'))

    def get_batch_no(self):
        # TODO: change to object class
        if 'batch_no' not in self.data:
            return ''
        if len(self.data['batch_no']) == 0:
            return ''
        return self.data['batch_no'][0]['number']

    def get_birth_date(self):
        return format_utc_to_local(self.data.get('birth_date'))

    def get_books(self):
        books = []
        if self.books.get('book_none', False):
            books.append('None')
        if self.books.get('volume1', False):
            books.append('Vol 1.')
        if self.books.get('volume2', False):
            books.append('Vol 2.')
        return ','.join(books)
    
    def get_branch_name(self):
        # TODO: change to object class
        if 'branch' not in self.data:
            return ''
        if len(self.data['branch']) == 0:
            return ''
        return self.data['branch'][0]['name']
        
    def get_contact_person_name(self):
        # TODO: change to object class
        if 'contact_person' not in self.data:
            return ''
        if len(self.data['contact_person']) == 0:
            return ''
        return self.data['contact_person'][0]['fname'] + " " + self.data['contact_person'][0]['lname']

    def get_fle(self):
        return convert_decimal128_to_decimal(self.document.get('fle'))

    def get_full_name(self, reverse=False):
        if reverse:
            if self.mname:
                return self.lname + " " + self.mname + " " + self.fname
            else:
                return self.lname + " " + self.fname
        else:
            if self.mname:
                return self.fname + " " + self.mname + " " + self.lname
            else:
                return self.fname + " " + self.lname

    def get_id(self):
        return self.data['_id']

    def get_id_materials(self):
        pass
    
    def get_is_deposited(self):
        if convert_decimal128_to_decimal(self.amount) == self.get_amount_deposit():
            deposit = "Yes"
        else:
            deposit = "No"
        return deposit
    
    def get_payment_mode(self):
        payment_mode = ""
        if self.payment_mode == 'full_payment':
            payment_mode = "Full Payment"
        elif self.payment_mode == 'installment':
            payment_mode = "Installment"
        elif self.payment_mode == 'premium':
            payment_mode = "Premium Payment"
        elif self.payment_mode == 'full_payment_promo':
            payment_mode = "Full Payment - Promo"
        elif self.payment_mode == 'installment_promo':
            payment_mode = "Installment - Promo"
        elif self.payment_mode == 'premium_promo':
            payment_mode = "Premium Payment - Promo"
        elif self.payment_mode == "refund":
            payment_mode = "Refunded"
        return payment_mode

    def get_payment_status(self):
        if self.get_balance() <= 0.00:
            return 'PAID'
        return 'NOT PAID'
    
    def get_registration_date(self, date_format="%B %d, %Y %I:%M %p"):
        return format_utc_to_local(self.data.get('registration_date'), date_format=date_format)

    def get_registration_no(self):
        return self.data.get('full_registration_number', '')

    def get_reviewers(self):
        reviewers: list = []
        if self.reviewers.get('reading', False):
            reviewers.append("Reading")
        if self.reviewers.get('listening', False):
            reviewers.append("Listening")
        if len(reviewers) == 0:
            return "None"
        return ','.join(reviewers)

    def get_session(self):
        return self.data.get('session', '')

    def get_sle(self):
        return convert_decimal128_to_decimal(self.document.get('sle'))

    def get_uniform(self):
        if self.uniforms is None:
            return "None"

        uniform = ""
        if self.uniforms['uniform_none']:
            uniform = "None"
        elif self.uniforms['uniform_xs']:
            uniform = "XS"
        elif self.uniforms['uniform_s']:
            uniform = "S"
        elif self.uniforms['uniform_m']:
            uniform = "M"
        elif self.uniforms['uniform_l']:
            uniform = "L"
        elif self.uniforms['uniform_xl']:
            uniform = "XL"
        elif self.uniforms['uniform_xxl']:
            uniform = "XXL"
        return uniform
    
    def has_id_card(self):
        if self.id_materials.get('id_card', False):
            return True
        else:
            return False

    def has_id_lace(self):
        if self.id_materials.get('id_lace', False):
            return True
        else:
            return False


class Registration(Base, Admin):
    meta = {
        'collection': 'lms_registrations',
        'strict': False
    }

    __tablename__ = 'lms_registrations'
    __amname__ = 'registration'
    __amdescription__ = 'Register'
    __amicon__ = 'pe-7s-add-user'
    __view_url__ = 'lms.register'

    registration_number = db.IntField()
    full_registration_number = db.StringField()
    schedule = db.StringField()
    branch = db.ReferenceField('Branch')
    batch_number = db.ReferenceField('Batch')
    amount = db.DecimalField()
    balance = db.DecimalField()
    contact_person = db.ReferenceField('User')
    fname = db.StringField()
    mname = db.StringField()
    lname = db.StringField()
    gender = db.StringField()
    suffix = db.StringField()
    address = db.StringField()
    passport = db.StringField()
    contact_number = db.StringField()
    email = db.StringField()
    birth_date = db.DateTimeField()
    books = db.DictField()
    uniforms = db.DictField()
    id_materials = db.DictField()
    reviewers = db.DictField()
    payment_mode = db.StringField()
    status = db.StringField()
    is_oriented = db.BooleanField()
    date_oriented = db.DateTimeField()
    orientator = db.ReferenceField('Orientator')
    # payments = db.ListField()
    # payments = db.EmbeddedDocumentListField(Payment)
    # payments = db.ListField(db.EmbeddedDocumentField(Payment))
    e_registration = db.StringField()
    e_reg_password = db.StringField()
    referred_by = db.ReferenceField('Registration')
    level = db.StringField()
    fle = db.DecimalField()
    sle = db.DecimalField()
    registration_date = db.DateTimeField()
    amount_deposit = db.DecimalField()
    copy_payments = db.ListField()
    civil_status = db.StringField()
    gender = db.StringField()
    session = db.StringField()
    is_examinee = db.BooleanField()
    is_passer = db.BooleanField()
    
    def get_birth_date(self):
        return format_utc_to_local(self.birth_date)
    

    def get_payment_mode(self):
        payment_mode = ""
        if self.payment_mode == 'full_payment':
            payment_mode = "Full Payment"
        elif self.payment_mode == 'installment':
            payment_mode = "Installment"
        elif self.payment_mode == 'premium':
            payment_mode = "Premium Payment"
        elif self.payment_mode == 'full_payment_promo':
            payment_mode = "Full Payment - Promo"
        elif self.payment_mode == 'installment_promo':
            payment_mode = "Installment - Promo"
        elif self.payment_mode == 'premium_promo':
            payment_mode = "Premium Payment - Promo"
        elif self.payment_mode == "refund":
            payment_mode = "Refunded"
        return payment_mode

    def get_is_deposited(self):
        if self.amount == self.amount_deposit:
            deposit = "Yes"
        else:
            deposit = "No"
        return deposit

    @property
    def age(self):
        today = datetime.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
    
    def set_registration_date(self):
        date_string = str(datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S"))
        naive = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        local_dt = TIMEZONE.localize(naive, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        self.registration_date = utc_dt

    @property
    def registration_date_local_string(self):
        local_datetime = ''
        if self.registration_date is not None:
            local_datetime = self.registration_date.replace(tzinfo=pytz.utc).astimezone(TIMEZONE)
            return local_datetime.strftime("%B %d, %Y %I:%M %p")
            
        return local_datetime

    @property
    def registration_date_local_date(self):
        if self.registration_date is not None:
            local_datetime = self.registration_date.replace(tzinfo=pytz.utc).astimezone(TIMEZONE)
            date_string = local_datetime.strftime("%Y-%m-%d %H:%M:%S")
            registration_date = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
            return registration_date

        return None

    @property
    def oriented_date_local(self):
        local_datetime = ''
        if self.date_oriented is not None:
            local_datetime = self.date_oriented.replace(tzinfo=pytz.utc).astimezone(TIMEZONE)
            return local_datetime.strftime("%B %d, %Y %I:%M %p")
            
        return local_datetime

    @property
    def full_name(self):
        if self.mname:
            return self.fname + " " + self.mname + " " + self.lname
        
        return self.fname + " " + self.lname


    def get_reviewers(self):
        reviewers: list = []
        if self.reviewers.get('reading', False):
            reviewers.append("Reading")
        if self.reviewers.get('listening', False):
            reviewers.append("Listening")
        if len(reviewers) == 0:
            return "None"
        return ','.join(reviewers)

    def update_books_from_form(self, books):
        self.books = {
            'book_none': True if 'book_none' in books else False,
            'volume1': True if 'volume1' in books else False,
            'volume2': True if 'volume2' in books else False,
        }

    def update_uniform_from_form(self, uniforms):
        self.uniforms = {
            'uniform_none': True if 'uniform_none' in uniforms else False,
            'uniform_xs': True if 'uniform_xs' in uniforms else False,
            'uniform_s': True if 'uniform_s' in uniforms else False,
            'uniform_m': True if 'uniform_m' in uniforms else False,
            'uniform_l': True if 'uniform_l' in uniforms else False,
            'uniform_xl': True if 'uniform_xl' in uniforms else False,
            'uniform_xxl': True if 'uniform_xxl' in uniforms else False,
        }

    def update_id_materials(self, id_materials):
        self.id_materials = {
            'id_card': True if 'id_card' in id_materials else False,
            'id_lace': True if 'id_lace' in id_materials else False,
        }
        
    def update_reviewers(self, reviewers):
        self.reviewers = {
            'reading': True if 'reading' in reviewers else False,
            'listening': True if 'listening' in reviewers else False,
        }

class Teacher(Base, Admin):
    meta = {
        'collection': 'auth_users',
        'strict': False,
    }

    __tablename__ = 'auth_users'
    __amname__ = 'teacher'
    __amdescription__ = 'Teacher'
    __amicon__ = 'pe-7s-user'
    __view_url__ = 'lms.teachers'

    fname = db.StringField()
    lname = db.StringField()

    @property
    def name(self):
        return f"{self.fname} {self.lname}"

class Branch(Base, Admin):
    meta = {
        'collection': 'lms_branches',
        'strict': False,
    }

    __tablename__ = 'lms_branches'
    __amname__ = 'branch'
    __amdescription__ = 'Branches'
    __amicon__ = 'pe-7s-culture'
    __view_url__ = 'lms.branches'

    name = db.StringField()
    address = db.StringField()
    teacher = db.ReferenceField('Teacher')
    maintaining_balance = db.DecimalField()
    email_address = db.StringField()
    landline = db.StringField()
    
    @property
    def city(self): 
        return self.name.replace('BRANCH', '')
        
class Batch(Base, Admin):
    meta = {
        'collection': 'lms_batches',
        'strict': False,
    }

    __tablename__ = 'lms_batches'
    __amname__ = 'batch'
    __amdescription__ = 'Batch Numbers'
    __amicon__ = 'pe-7s-date'
    __view_url__ = 'lms.batches'

    number = db.StringField(unique=True)
    branch = db.ReferenceField('Branch')
    start_date = db.DateTimeField()


class Partner(Admin):
    __tablename__ = 'auth_user'
    __amname__ = 'partner'
    __amdescription__ = 'Partners'
    __amicon__ = 'pe-7s-user'
    __view_url__ = 'lms.contact_persons'

class Orientator(Base, Admin):
    meta = {
        'collection': 'lms_orientators',
        'strict': False,
    }

    __tablename__ = 'lms_orientators'
    __amname__ = 'orientator'
    __amdescription__ = 'Orientators'
    __amicon__ = 'pe-7s-tools'
    __view_url__ = 'lms.contact_persons'

    fname = db.StringField()
    lname = db.StringField()
    is_active = db.BooleanField()

    @property
    def name(self):
        return self.fname


class InboundOutbound(db.EmbeddedDocument):
    # custom_id = db.StringField(primary_key=True)
    _id = db.ObjectIdField( required=True, default=lambda: ObjectId())
    brand = db.StringField()
    price = db.DecimalField()
    quantity = db.IntField()
    total_amount = db.DecimalField()
    remarks = db.StringField()
    date = db.DateTimeField()
    withdraw_by =db.StringField()
    confirm_by = db.ReferenceField('User')

    @property
    def id(self):
        if not self._id:
            return ''

        return str(self._id)

class Inventory(Base, Admin):
    meta = {
        'collection': 'lms_inventories',
        'strict': False,
    }
    __amname__ = 'inventory'
    __amdescription__ = 'Inventory'
    __amicon__ = 'pe-7s-back-2'

    price = db.DecimalField()
    description = db.StringField()
    maintaining = db.IntField()
    released = db.IntField()
    remaining = db.IntField()
    total_replacement = db.IntField()
    type = db.StringField()
    branch = db.ReferenceField('Branch')
    uom = db.StringField()
    qty = db.StringField()
    purchase_date = db.DateTimeField()
    transactions = db.EmbeddedDocumentListField(InboundOutbound)
    is_for_sale = db.BooleanField()

    @property
    def name(self):
        return self.description


class Marketer(Admin):
    __tablename__ = 'auth_users'
    __amname__ = 'marketer'
    __amdescription__ = 'Marketers'
    __amicon__ = 'pe-7s-user'
    __view_url__ = 'lms.marketers'

class Member(Admin):
    __tablename__ = 'lms_members'
    __amname__ = 'member'
    __amdescription__ = 'Student Records'
    __amicon__ = 'pe-7s-users'
    __view_url__ = 'lms.members'


class Earning(Admin):
    __tablename__ = 'lms_earnings'
    __amname__ = 'earning'
    __amdescription__ = 'Earnings'
    __amicon__ = 'pe-7s-cash'
    __view_url__ = 'lms.earnings'


class Secretary(Admin):
    __tablename__ = 'auth_users'
    __amname__ = 'secretary'
    __amdescription__ = 'Secretary'
    __amicon__ = 'pe-7s-user'
    __view_url__ = 'lms.secretaries'


class OrientationAttendance(Admin):
    __tablename__ = 'lms_orientation_attendance'
    __amname__ = 'orientation_attendance'
    __amdescription__ = 'Orientation Attendance'
    __amicon__ = 'pe-7s-note2'
    __view_url__ = 'lms.orientation_attendance'



class Dashboard(Admin):
    __amname__ = 'dashboard'
    __amdescription__ = 'Dashboard'
    __amicon__ = 'pe-7s-graph2'
    __view_url__ = 'lms.dashboard'


class Equipment(Admin):
    __tablename__ = 'lms_inventories'
    __amname__ = 'equipment'
    __amdescription__ = 'Equipments'
    __amicon__ = 'pe-7s-tools'
    __view_url__ = 'lms.equipments'


class CashFlow(Base, Admin):
    meta = {
        'collection': 'lms_bank_statements',
        'strict': False,

    }
    
    __tablename__ = 'lms_bank_statements'
    __amname__ = 'cash_flow'
    __amdescription__ = 'Cash Flow'
    __amicon__ = 'pe-7s-refresh-2'
    __view_url__ = 'lms.cash_flow'
    
    date_deposit = db.DateField()
    bank_name = db.StringField()
    account_no = db.StringField()
    account_name = db.StringField()
    amount = db.DecimalField()
    from_what = db.StringField()
    by_who = db.StringField()
    type = db.StringField()
    branch = db.ReferenceField('Branch')
    balance = db.DecimalField()
    group = db.IntField()
    payments = db.EmbeddedDocumentListField(Payment)
    remarks = db.StringField()
    receipt_path = db.StringField()

    def set_deposit_date(self):
        date_string = str(datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S"))
        naive = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        local_dt = TIMEZONE.localize(naive, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        self.date_deposit = utc_dt

    @property
    def deposit_date_local_string(self):
        local_datetime = ''
        if self.date_deposit is not None:
            local_datetime = self.date_deposit.replace(tzinfo=pytz.utc).astimezone(TIMEZONE)
            return local_datetime.strftime("%B %d, %Y %I:%M %p")
            
        return local_datetime

    # @property
    # def registration_date_local_date(self):
    #     if self.registration_date is not None:
    #         local_datetime = self.registration_date.replace(tzinfo=pytz.utc).astimezone(TIMEZONE)
    #         date_string = local_datetime.strftime("%Y-%m-%d %H:%M:%S")
    #         registration_date = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    #         return registration_date

    #     return None

class Accounting(Base):
    meta = {
        'collection': 'lms_accounting',
        'strict': False,
    }
    
    branch = db.ReferenceField('Branch')
    total_gross_sale = db.DecimalField()
    final_fund1 = db.DecimalField()
    final_fund2 = db.DecimalField()
    profits = db.ListField()
    active_group = db.IntField()

class StudentSupply(Base, Admin):
    meta = {
        'collection': 'lms_student_supplies',
        'strict': False,
    }
    __amname__ = 'inventory'
    __amdescription__ = 'Inventory'
    __amicon__ = 'pe-7s-back-2'
    __tablename__ = 'lms_student_supplies'

    price = db.DecimalField()
    description = db.StringField()
    maintaining = db.IntField()
    released = db.IntField()
    remaining = db.IntField()
    total_replacement = db.IntField()
    type = db.StringField()
    branch = db.ReferenceField('Branch')
    uom = db.StringField()
    qty = db.StringField()
    purchase_date = db.DateTimeField()
    transactions = db.EmbeddedDocumentListField(InboundOutbound)
    is_for_sale = db.BooleanField()
    replacent = db.IntField()

    @property
    def name(self):
        return self.description


class OfficeSupply(Base, Admin):
    meta = {
        'collection': 'lms_office_supplies',
        'strict': False,
    }
    __amname__ = 'inventory'
    __amdescription__ = 'Office Supply'
    __amicon__ = 'pe-7s-back-2'
    __tablename__ = 'lms_office_supplies'

    price = db.DecimalField()
    description = db.StringField()
    maintaining = db.IntField()
    released = db.IntField()
    remaining = db.IntField()
    total_replacement = db.IntField()
    type = db.StringField()
    branch = db.ReferenceField('Branch')
    uom = db.StringField()
    qty = db.StringField()
    purchase_date = db.DateTimeField()
    transactions = db.EmbeddedDocumentListField(InboundOutbound)
    is_for_sale = db.BooleanField()
    replacement = db.IntField()

    @property
    def name(self):
        return self.description


class Utilities(Admin):
    __tablename__ = 'lms_inventories'
    __amname__ = 'utilities'
    __amdescription__ = 'Utilities'
    __amicon__ = 'pe-7s-tools'
    __view_url__ = 'lms.utilities'


class CashOnHand(Admin):
    __tablename__ = 'lms_cash_on_hand'
    __amname__ = 'cash_on_hand'
    __amdescription__ = 'Cash On Hand'
    __amicon__ = 'pe-7s-cash'
    __view_url__ = 'lms.cash_on_hand'


class FundWallet(Admin, Base):
    meta = {
        'collection': 'lms_fund_wallet_transactions',
        'strict': False,
    }

    __tablename__ = 'lms_fund_wallet_transactions'
    __amname__ = 'fund_wallet'
    __amdescription__ = 'Fund Wallet'
    __amicon__ = 'pe-7s-wallet'
    __view_url__ = 'lms.fund_wallet'

    type = db.StringField()
    running_balance = db.DecimalField()
    date = db.DateTimeField()
    branch = db.ReferenceField('Branch')
    bank_name = db.StringField()
    transaction_no = db.StringField()
    sender = db.StringField()
    receiver = db.StringField()
    amount_received = db.DecimalField()
    remarks = db.StringField()
    # Expenses
    category = db.StringField()
    description = db.StringField()
    account_no = db.StringField()
    billing_month_from = db.DateTimeField()
    billing_month_to = db.DateTimeField()
    settled_by = db.StringField()
    total_amount_due = db.DecimalField()
    qty = db.IntField()
    unit_price = db.DecimalField()


class Expenses(Base, Admin):
    meta = {
        'collection': 'lms_expenses_transactions',
        'strict': False,
    }
    
    __tablename__ = 'lms_expenses_transactions'
    __amname__ = 'expenses'
    __amdescription__ = 'Operating Expenses'
    __amicon__ = 'pe-7s-tools'
    __view_url__ = 'lms.expenses'

    date = db.DateTimeField()
    branch = db.ReferenceField('Branch')
    category = db.StringField()
    account_no = db.StringField()
    billing_month = db.StringField()
    settled_by = db.StringField()
    total_amount_due = db.DecimalField()
    remarks = db.StringField()


class Item(db.EmbeddedDocument):
    meta = {
        'strict': False,
    }

    item = db.ReferenceField("Inventory")
    qty = db.IntField()
    price = db.DecimalField()
    amount = db.DecimalField()


class StoreRecords(Base, Admin):
    meta = {
        'collection': 'lms_store_buyed_items',
        'strict': False,
    }

    __tablename__ = 'lms_store_buyed_items'
    __amname__ = 'store_records'
    __amdescription__ = 'Store Records'
    __amicon__ = 'pe-7s-notebook'
    __view_url__ = 'lms.store_records'

    branch : Branch = db.ReferenceField('Branch')
    client_id : Registration = db.ReferenceField('Registration')
    items = db.EmbeddedDocumentListField(Item)
    total_amount = db.DecimalField()
    uniforms = db.IntField()
    id_lace = db.IntField()
    id_card =db.IntField()
    module_1 = db.IntField()
    module_2 = db.IntField()
    reviewer_l = db.IntField()
    reviewer_r = db.IntField()
    deposited = db.StringField()

    @property
    def local_datetime(self):
        if type(self.created_at) == datetime:
            local_datetime = self.created_at.replace(tzinfo=pytz.utc).astimezone(TIMEZONE).strftime("%B %d, %Y")
        elif type(self.created_at == str):
            to_date = datetime.strptime(self.created_at, "%Y-%m-%d")
            local_datetime = to_date.strftime("%B %d, %Y")
        else: 
            local_datetime = ''

        return local_datetime



class BuyItems(Admin):
    __tablename__ = 'lms_buy_items'
    __amname__ = 'buy_items'
    __amdescription__ = 'Buy Items'
    __amicon__ = 'pe-7s-calculator'
    __view_url__ = 'lms.buy_items'


class Accommodation(Base, Admin):
    meta = {
        'collection': 'lms_accommodations',
        'strict': False
    }

    __tablename__ = 'lms_accommodations'
    __amname__ = 'accommodation'
    __amdescription__ = 'Accommodation'
    __amicon__ = 'pe-7s-bookmarks'
    __view_url__ = 'lms.accommodation'

    client_id = db.ReferenceField('Registration')
    branch = db.ReferenceField('Branch')
    date_from = db.DateField()
    date_to = db.DateField()
    days = db.IntField()
    total_amount = db.DecimalField()
    remarks = db.StringField()
    deposited = db.StringField()

    @property
    def local_datetime(self):
        if type(self.created_at) == datetime:
            local_datetime = self.created_at.replace(tzinfo=pytz.utc).astimezone(TIMEZONE).strftime("%B %d, %Y")
        elif type(self.created_at == str):
            to_date = datetime.strptime(self.created_at, "%Y-%m-%d")
            local_datetime = to_date.strftime("%B %d, %Y")
        else: 
            local_datetime = ''

        return local_datetime
        
        
class Settings(Admin):
    __tablename__ = 'lms_buy_items'
    __amname__ = 'buy_items'
    __amdescription__ = 'Buy Items'
    __amicon__ = 'pe-7s-calculator'
    __view_url__ = 'lms.buy_items'

class OurTestimony(Base, Admin):
    meta = {
        'collection': 'lms_our_testimonies',
        'strict': False,
    }

    __tablename__ = 'lms_our_testimonies'
    __amname__ = 'our_testimonies'
    __amdescription__ = 'Our Testimonies'
    __amicon__ = 'pe-7s-file'
    __view_url__ = 'lms.pages_home'

    title = db.StringField()
    description = db.StringField()
    image = db.StringField()

    @property
    def oldimage(self):
        return self.image