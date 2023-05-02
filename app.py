from flask import Flask, request, render_template, redirect, url_for
import mysql.connector
import os


class MyApp(Flask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.firstPageData = {}  # Dict that storing first page info
        self.secondPageData = {}  # Dict that storing second page info
        self.pdf = ''  # Storing pdf file path / binary data
        self.db = mysql.connector.connect(
            host='localhost', user='root', password='dbpass', database='webform')  # Connect to database
        self.personalInfo = ""  # Storing personal info
        self.referenceContacts = []  # A list of reference contacts
        self.workingInfo = ""  # Storing working info
        self.bakingInfo = ""  # Storing bank info
        self.add_url_rule('/', view_func=self.index,
                          methods=['GET', 'POST'])  # Bind self.index to /
        # Bind self.submitFirstPage to /submitFirstPage
        self.add_url_rule('/submitFirstPage',
                          view_func=self.submitFirstPage, methods=['POST'])
        # Bind self.page2 to /page2
        self.add_url_rule('/page2', view_func=self.page2)
        self.add_url_rule('/submit', view_func=self.submit,
                          methods=['POST'])  # Bind self.submit to /submit
        # Bind self.saveSecond to /saveSecond
        self.add_url_rule(
            '/saveSecond', view_func=self.saveSecond, methods=['POST'])
        self.add_url_rule(
            '/firstPage', view_func=self.getFirstPageData, methods=['POST'])  # Bind self.getFirstPageData to /firstPage
        self.add_url_rule(
            '/secondPage', view_func=self.getSecondPageData, methods=['POST'])  # Bind self.getSecondPageData to /secondPage

    # Main Page
    def index(self):
        if request.form:
            self.secondPageData = request.form
        return render_template('Page1.html')

    # Second page
    def page2(self):
        return render_template('Page2.html')

    # Submit First Page Handler
    def submitFirstPage(self):
        if self.firstPageData == {}:
            self.firstPageData = dict(request.form)
        self.firstPageData['gender'] = 'Male' if int(
            self.firstPageData['NRIC']) % 2 == 1 else 'Female'
        self.restructureFirstPageInfo()
        print(self.firstPageData)
        return redirect(url_for('page2'))

    # Submit Second Page Handler
    def submit(self):
        print(request.form)
        print(request.files)
        self.secondPageData = request.form
        self.restructureSecondPageInfo()
        return '<h1>Submitted, please wait</h1>'

    # Save Second Page Data
    def saveSecond(self):
        self.secondPageData = request.json
        print(self.secondPageData)
        return redirect(url_for('index'))

    # Get First Page Data
    def getFirstPageData(self):
        return self.firstPageData

    # Get Second Page Data
    def getSecondPageData(self):
        return self.secondPageData

    # Restructure First Page Data into a string
    def restructureFirstPageInfo(self):
        data = self.firstPageData
        self.personalInfo = f"{data['NRIC']}, {data['name']}, {data['countryCode'] + data['phoneNumber']}, {data['email']}, {data['title']}, {data['gender']}, {data['race'] if data['race'] != '' else data['otherRace']}, {data['maritalStatus']}, {data['bumiornon']}, {data['address']}, {data['numOfYear']}, {data['ownership']}, {data['stayRegisterAddress']} {data['noStayRegisterAddress'] if data['stayRegisterAddress'] == 'No' else 'None'}, {data['productType']}, {data['newusedrecon']}, {data['usedNumberPlate'] if data['newusedrecon'] == 'Used' else data['reconNumberPlate'] if data['newusedrecon'] == 'Recon' else 'None'}, {data['tenure']}"

        referenceContact1 = [f"{data['NRIC']}", f"{data['referenceName1']}",
                             f"{data['referenceCountryCode1'] + data['referencePhoneNum1']}", f"{data['stayWithReference1']}", f"{data['referenceRelation1']}"]

        referenceContact2 = [f"{data['NRIC']}", f"{data['referenceName2']}",
                             f"{data['referenceCountryCode2'] + data['referencePhoneNum2']}", f"{data['stayWithReference2']}", f"{data['referenceRelation2']}"]

        self.referenceContacts.append(referenceContact1)
        self.referenceContacts.append(referenceContact2)

    # Restructure Second Page Data into a string
    def restructureSecondPageInfo(self):
        data = self.secondPageData
        employmentStatus = data['employmentStatus']
        status = ''
        print(data)
        if employmentStatus == 'employed':
            status = data['employmentStatus']
        elif employmentStatus == 'other':
            status = data['otherIncomeSource']
            if status == 'yes':
                status = data['otherIncomeSourceOther']
        elif employmentStatus == 'student':
            status = 'None'
        elif employmentStatus == 'self-employed' and data['selfEmployedStatus'] != 'other':
            status = data['selfEmployedStatus']
        else:
            status = data['selfEmployedOther']

        self.workingInfo = f"{self.firstPageData['NRIC']}, {data['employmentStatus']}, {status}, {data['position'] if data['employmentStatus'] != 'student' else 'None'}, {data['department'] if data['employmentStatus'] != 'student' else 'None'}, {data['businessNature']}, {data['companyName']}, {data['companyCountryCode'] + data['companyPhoneNumber']}, {data['workinginsingapore']}, {data['companyAddress']}, {data['whenJoinedCompany']}, {data['grossSalary'] + '.' + data['grossSalaryDecimal']}, {data['salaryTerm']}"

        self.bakingInfo = f"{self.firstPageData['NRIC']}, {data['bankName']}, {data['bankAccountNumber']}, {data['typeOfAccount'] if data['typeOfAccount'] != 'other' else data['typeOfAccountOther']}, {data['bestContactTime']}, {data['motorLicense']}, {data['licenseType'] if data['motorLicense'] == 'hasLicense' else 'None'}, {data['howToKnowMotosing']}"


app = MyApp(__name__)
if __name__ == '__main__':
    app.run(root_path=os.path.dirname(os.path.abspath(__file__)))
print(__file__)
