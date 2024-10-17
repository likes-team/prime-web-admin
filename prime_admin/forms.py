from flask_wtf import FlaskForm
from app.admin.forms import AdminTableForm, AdminEditForm, AdminInlineForm, AdminField
from wtforms.validators import DataRequired
from wtforms import StringField, SelectField, DecimalField, DateField



class ExpensesForm(AdminTableForm):
    from .models import Inventory

    __table_columns__ = [
        'date', 'description', 'price', 'quantity', 'subtotal'
    ]

    __heading__ = "Operating Expenses"

    inventory = AdminField(label="Description", validators=[DataRequired()], model=Inventory)
    quantity = AdminField(label='Quantity', validators=[DataRequired()], type='number')
    price = AdminField(label='Price', validators=[DataRequired()], type='numeric')
    uom = AdminField(label='Unit of Measurement', required=False)

    @property
    def fields(self):
        return [
            [self.inventory, self.price],
            [self.quantity, self.uom]
            ]


class OrientationAttendanceForm(AdminTableForm):
    __table_columns__ = [
        'Branch',
        'full name',
        'contact no',
        'contact person',
        'orientator',
        'Date',
        'Actions'
    ]

    __heading__ = "Orientation Attendance"

    contact_person = StringField()
    orientator = StringField()
    branch = StringField()
    referred_by = StringField()

    @property
    def fields(self):
        return []


class CashFlowSecretaryForm(AdminTableForm):
    __table_columns__ = [
        'id',
        'Date',
        'Bank name',
        'account no.',
        'account name',
        'Deposit amount',
        'from',
        'by who',
        'remarks',
        'group',
        'actions'
    ]

    __heading__ = "Cash Flow"

    @property
    def fields(self):
        return []


class CashFlowAdminForm(AdminTableForm):
    __table_columns__ = [
        'id',
        'Date',
        'Deposit',
        'from',
        'withdraw',
        'balance',
        'to',
        'withdraw from',
        'bank name',
        'account no.',
        'account name',
        'by who',
        'remarks',
        'group',
        'actions'
    ]

    __heading__ = "Cash Flow"

    @property
    def fields(self):
        return []
class DepositForm(FlaskForm):
    date_deposit = DateField()
    bank_name = StringField()
    account_no = StringField()
    account_name = StringField()
    amount = DecimalField()
    from_what = StringField()
    by_who = StringField()
    remarks = StringField()

class WithdrawForm(FlaskForm):
    date_deposit = DateField()
    bank_name = StringField()
    account_no = StringField()
    account_name = StringField()
    amount = DecimalField()
    from_what = StringField()
    to_what = StringField()
    by_who = StringField()    
    branch = StringField()    
    remarks = StringField()


class InventoryForm(AdminTableForm):
    from prime_admin.models import Branch

    __table_columns__ = [
        'Actions','Description', 'UOM', 'QTY', "Maintaining Materials",
        '1' ,'2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20','21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31',
        'total used', 'Remaining Materials','Total replacement', 'Price', 'Amount'
    ]

    __heading__ = "Inventories"

    description = AdminField(label="Description", validators=[DataRequired()])
    maintaining = AdminField(label="Maintaining Materials", validators=[DataRequired()], type='number')
    remaining = AdminField(label="Quantity", validators=[DataRequired()], type='number')
    price = AdminField(label="Price", validators=[DataRequired()], type='decimal')
    uom = AdminField(label="UOM", validators=[DataRequired()])
    branch = AdminField(label="Branch", validators=[DataRequired()], model=Branch)
    purchase_date = AdminField(label="Purchase Date", validators=[DataRequired()], type='date')

    @property
    def fields(self):
        return [
            [self.branch, self.description],
            [self.price, self.uom],
            [self.maintaining, self.remaining],
            [self.purchase_date]
            ]



class BatchForm(AdminTableForm):
    from prime_admin.models import Branch

    __table_columns__ = ['id','Status', 'Number', 'Branch', 'Start Date', 'created by','Created at', 'updated by','updated at']
    __heading__ = "Batches"

    number = AdminField(label="Number", validators=[DataRequired()])
    branch = AdminField(label="Branch", validators=[DataRequired()], model=Branch)
    start_date = AdminField(label="Start Date", validators=[DataRequired()], type='date')

    @property
    def fields(self):
        return [
            [self.number, self.branch],
            [self.start_date]
            ]


class BatchEditForm(AdminEditForm):
    from prime_admin.models import Branch

    __heading__ = "Update existing data"

    number = AdminField(label="Number", validators=[DataRequired()])
    # branch = AdminField(label="Branch", validators=[DataRequired()], model=Branch)
    start_date = AdminField(label="Start Date", validators=[DataRequired()], type='date')

    @property
    def fields(self):
        return [
            [self.number, self.start_date]
            ]



class SecretaryForm(AdminTableForm):
    from prime_admin.models import Branch

    __table_columns__ = ['First Name', 'Last Name', 'Branch', 'created by','Created at', 'updated by','updated at']
    __heading__ = "Secretaries"

    fname = AdminField(label="First Name", validators=[DataRequired()])
    lname = AdminField(label="Last Name", validators=[DataRequired()])
    branch = AdminField(label="Branch", validators=[DataRequired()], model=Branch)
    username = AdminField(label='Username', validators=[DataRequired()])
    email = AdminField(label='Email', type='email',required=False)

    @property
    def fields(self):
        return [
            [self.fname, self.lname],
            [self.username, self.email],
            [self.branch]
            ]


class SecretaryEditForm(AdminEditForm):
    from prime_admin.models import Branch

    __heading__ = "Update existing data"

    fname = AdminField(label="First Name", validators=[DataRequired()])
    lname = AdminField(label="Last Name", validators=[DataRequired()])
    branch = AdminField(label="Branch", validators=[DataRequired()], model=Branch)
    username = AdminField(label='Username', validators=[DataRequired()])
    email = AdminField(label='Email', type='email',required=False)

    @property
    def fields(self):
        return [
            [self.fname, self.lname],
            [self.username, self.email],
            [self.branch]
            ]


class BranchForm(AdminTableForm):
    from prime_admin.models import Teacher

    __table_columns__ = ['Name', 'created by','Created at', 'updated by','updated at']
    __heading__ = "Branches"

    name = AdminField(label="Name", validators=[DataRequired()])
    address = AdminField(label="Address", validators=[DataRequired()])
    teacher = AdminField(label="Teacher", model=Teacher)

    @property
    def fields(self):
        return [
            [self.name, self.address],
            [self.teacher]
        ]


class ContactPersonForm(AdminTableForm):
    __table_columns__ = ['First Name', 'Last Name', 'created by','Created at', 'updated by','updated at']
    __heading__ = "Partners"

    fname = AdminField(label="First Name", validators=[DataRequired()])
    lname = AdminField(label="Last Name", validators=[DataRequired()])
    
    @property
    def fields(self):
        return [[self.fname, self.lname]]


class BranchEditForm(AdminEditForm):
    from prime_admin.models import Teacher
    
    __heading__ = "Edit Branch"

    name = AdminField(label="Name", validators=[DataRequired()])
    address = AdminField(label="Address", validators=[DataRequired()])
    teacher = AdminField(label="Teacher", model=Teacher)

    @property
    def fields(self):
        return [
            [self.name, self.address],
            [self.teacher]
        ]


class BranchesInlineForm(AdminInlineForm):
    __table_id__ = 'tbl_branches_inline'
    __table_columns__ =[None, 'Branch', '','','','Action']
    __title__ = "current branches"
    __html__ = 'lms/branches_inline.html'


class AddBranchesInline(AdminInlineForm):
    __table_id__ = 'tbl_add_branches_inline'
    __table_columns__ =[None,'Branch', '','','','Action']
    __title__ = "add branches"
    __html__ = 'lms/add_branches_inline.html'


class ContactPersonEditForm(AdminEditForm):
    from .models import Branch

    __heading__ = "Edit Contact Person"

    username = AdminField(label='Username', validators=[DataRequired()])
    email = AdminField(label='Email', type='email',required=False)
    fname = AdminField(label="First Name", validators=[DataRequired()])
    lname = AdminField(label="Last Name", validators=[DataRequired()])
    is_employee = AdminField(label="Is Employee?", type='checkbox')
    is_teacher = AdminField(label="Is Teacher?", type='checkbox')
    branches_inline = BranchesInlineForm()
    add_branches_inline = AddBranchesInline()

    @property
    def inlines(self):
        return [self.branches_inline, self.add_branches_inline]

    @property
    def fields(self):
        return [[self.fname, self.lname], [self.username,self.email], [self.is_employee], [self.is_teacher]]


class PartnerForm(AdminTableForm):
    __table_columns__ = ['Name', 'created by','Created at', 'updated by','updated at']
    __heading__ = "Partners"

    name = AdminField(label="Name", validators=[DataRequired()])

    @property
    def fields(self):
        return [[self.name]]


class TrainingCenterForm(AdminTableForm):
    __table_columns__ = ['Name', 'created by','Created at', 'updated by','updated at']
    __heading__ = "Training Centers"

    name = AdminField(label="Name", validators=[DataRequired()])

    @property
    def fields(self):
        return [[self.name]]


class TrainingCenterEditForm(AdminEditForm):
    __heading__ = "Edit Training Center"

    name = AdminField(label="Name", validators=[DataRequired()])

    @property
    def fields(self):
        return [[self.name]]


class TeacherForm(AdminTableForm):
    __table_columns__ = ['First name', 'middle name', 'last name','created by','Created at', 'updated by','updated at']
    __heading__ = "Teachers"

    fname = AdminField(label="First name",validators=[DataRequired()])
    lname = AdminField(label="Last name",validators=[DataRequired()])
    mname = AdminField(label="Middle name",required=False)

    @property
    def fields(self):
        return [[self.fname, self.mname, self.lname]]


class TeacherEditForm(AdminEditForm):
    __heading__ = 'Edit teacher'

    fname = AdminField(label="First name",validators=[DataRequired()])
    lname = AdminField(label="Last name",validators=[DataRequired()])
    mname = AdminField(label="Middle name",required=False)

    @property
    def fields(self):
        return [[self.fname, self.mname, self.lname]]


class StudentForm(AdminTableForm):
    __table_columns__ = ['First name', 'middle name', 'last name', 'created by','Created at', 'updated by','updated at']
    __heading__ = "Students"

    fname = AdminField(label="First name",validators=[DataRequired()])
    lname = AdminField(label="Last name",validators=[DataRequired()])
    mname = AdminField(label="Middle name",required=False)

    @property
    def fields(self):
        return [[self.fname, self.mname, self.lname]]


class StudentEditForm(AdminEditForm):
    __heading__ = 'Edit student'

    fname = AdminField(label="First name",validators=[DataRequired()])
    lname = AdminField(label="Last name",validators=[DataRequired()])
    mname = AdminField(label="Middle name",required=False)

    @property
    def fields(self):
        return [[self.fname, self.mname, self.lname]]


class RegistrationForm(FlaskForm):
    from .models import Batch
    
    batch_number = AdminField(label='Batch Number', validators=[DataRequired()], model=Batch)

    schedule = SelectField('Schedule',choices=[
        ('WDC','WDC'), ('SDC', 'SDC'), ('SAT', 'SAT')
    ])

    branch = SelectField('Branch', choices=[
        ('cebu', 'Cebu'),
        ('tacloban', 'Tacloban'),
        ('bohol', 'Bohol'),
        ('palawan', 'Palawan')
    ])

    amount = DecimalField()
    contact_person = StringField()
    fname = StringField()
    mname = StringField()
    lname = StringField()
    suffix = StringField()
    address = StringField()
    passport = StringField()
    contact_number = StringField()
    email = StringField()
    birth_date = DateField()
    book = StringField()
    payment_mode = StringField()
    e_registration = StringField()
    civil_status = StringField()
    gender = StringField()
    session = StringField()
    thru = StringField()
    reference_no = StringField()
    payment_method = StringField()

class OurTestimoniesEditForm(AdminEditForm):
    
    __heading__ = "Edit Our Testimonies"

    title = AdminField(label="Title", validators=[DataRequired()])
    description = AdminField(label="Description", type="textarea", validators=[DataRequired()])
    image = AdminField(label="Image", type="image_with_preview", validators=[DataRequired()])
    oldimage = AdminField(label="Old Image", type="hidden")

    @property
    def fields(self):
        return [
            [self.title, self.description],
            [self.image],
            [self.oldimage],
        ]