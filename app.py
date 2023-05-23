from flask import Flask, request, render_template, redirect, url_for
from reportlab.pdfgen import canvas
from PyPDF2 import PdfMerger
import mysql.connector
import zipfile
import json
import os

# TODO:UPDATE BUSINESS OF NATURE
# TODO:UPDATE TYPE OF OCCUPATION 

class MyApp(Flask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config['UPLOAD_FOLDER'] = './pdfFiles'
        self.firstPageData = {}  # Dict that storing first page info
        self.secondPageData = {}  # Dict that storing second page info
        self.db = mysql.connector.connect(
            host='localhost', user='root', port='3306', password='Chong8182!', database='webform')
        # self.db = mysql.connector.connect(
        #     host='mysql', user='root', password='root', database='webform', port='3306')  # Connect to database
        self.cursor = self.db.cursor()
        self.personalInfo = ""  # Storing personal info
        self.referenceContacts = []  # A list of reference contacts
        self.workingInfo = ""  # Storing working info
        self.bankingInfo = ""  # Storing bank info
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
        return redirect(url_for('page2'))

    # Submit Second Page Handler
    def submit(self):
        pdfFiles = request.files.getlist('pdfFiles')
        zipFileName = f"./pdfFiles/{self.firstPageData['NRIC']}.zip"

        capturedPhoto = json.loads(request.form.get('capturedPhoto'))

        for i, photo_data_uri in enumerate(capturedPhoto):
            photo_pdf_path = f"./pdfFiles/photo_{i}.pdf"
            c = canvas.Canvas(photo_pdf_path)
            c.drawImage(photo_data_uri, 0, 0, 200, 200)
            c.save()

        pdfFiles.append(open(photo_pdf_path, 'rb'))

        merger = PdfMerger()

        for file in pdfFiles:
            merger.append(file)

        mergedPdfPath = f"./pdfFiles/{self.firstPageData['NRIC']}.pdf"
        merger.write(mergedPdfPath)
        merger.close()

        with zipfile.ZipFile(zipFileName, 'w') as zf:
            zf.write(mergedPdfPath, f"{self.firstPageData['NRIC']}.pdf")

        os.system('rm -rf ./pdfFiles/*.pdf')

        self.secondPageData = request.form
        self.restructureSecondPageInfo()
        query = f"INSERT INTO `Personal Info` VALUES ({self.personalInfo})"
        try:
            self.cursor.execute(query)
        except mysql.connector.Error as e:
            print(f"MySQL Error First Query: {e}")

        try:
            for i in self.referenceContacts:
                queryX = f"INSERT INTO `Reference Contact` (`NRIC`, `Name`, `Phone Number`, `Stay with user`, `Relation to user`) VALUES ({i})"
                self.cursor.execute(queryX)
        except mysql.connector.Error as e:
            print(f'MySQL Error Second Query: {e}')

        try:
            query2 = f"INSERT INTO `Working Info` (`NRIC`, `Employment Status`, `Status`, `Position`, `Department`, `Business Nature`, `Company Name`, `Company Phone Number`, `Working in Singapore`, `Company Address`, `When user joined company`, `Gross Salary`, `Salary Term`) VALUES ({self.workingInfo})"
            self.cursor.execute(query2)
        except mysql.connector.Error as e:
            print(f'MySQL Error Third Query: {e}')

        try:
            query3 = f"INSERT INTO `Banking Info` (`NRIC`, `Bank Name`, `Bank Account Number`, `Type Of Account`, `pdfFilePath`, `Best time to contact`, `Have license or not`, `License Type`, `How user know Motosing`) VALUES ({self.bankingInfo})"
            self.cursor.execute(query3)
        except mysql.connector.Error as e:
            print(f'Mysql Error Forth Query: {e}')

        self.db.commit()
        return '<h1>Submitted, please wait</h1>'

    # Save Second Page Data
    def saveSecond(self):
        self.secondPageData = request.json
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
        self.personalInfo = f"'{data['NRIC']}', '{data['name']}', '{data['countryCode'] + data['phoneNumber']}', '{data['email']}', '{data['title']}', '{data['gender']}', '{data['race'] if data['race'] != '' else data['otherRace']}', '{data['maritalStatus']}', '{data['bumiornon']}', '{data['address']}', '{data['numOfYear']}', '{data['ownership']}', '{data['stayRegisterAddress']}', '{data['noStayRegisterAddress'] if data['stayRegisterAddress'] == 'No' else 'None'}', '{data['productType']}', '{data['brand']}', '{data['modal']}', '{data['newusedrecon']}', '{data['usedNumberPlate'] if data['newusedrecon'] == 'Used' else data['reconNumberPlate'] if data['newusedrecon'] == 'Recon' else 'None'}', '{data['tenure']}'"

        referenceContact1 = f"'{data['NRIC']}', '{data['referenceName1']}', '{data['referenceCountryCode1'] + data['referencePhoneNum1']}', '{data['stayWithReference1']}', '{data['notStayWithApplicant1'] if data['stayWithReference1'] == 'no' else 'None'}', '{data['referenceRelation1']}'"

        referenceContact2 = f"'{data['NRIC']}', '{data['referenceName2']}', '{data['referenceCountryCode2'] + data['referencePhoneNum2']}', '{data['stayWithReference2']}', '{data['notStayWithApplicant2'] if data['stayWithReference2'] == 'no' else 'None'}', '{data['referenceRelation2']}'"

        self.referenceContacts.append(referenceContact1)
        self.referenceContacts.append(referenceContact2)

    # Restructure Second Page Data into a string
    def restructureSecondPageInfo(self):
        data = self.secondPageData
        employmentStatus = data['employmentStatus']
        status = ''
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

        self.workingInfo = f"'{self.firstPageData['NRIC']}', '{data['employmentStatus']}', '{status}', '{data['position'] if data['employmentStatus'] != 'student' else 'None'}', '{data['department'] if data['employmentStatus'] != 'student' else 'None'}', '{data['businessNature']}', '{data['companyName']}', '{data['companyCountryCode'] + data['companyPhoneNumber']}', '{data['workinginsingapore']}', '{data['companyAddress']}', '{data['whenJoinedCompany']}', 'RM {data['grossSalary'] + '.' + data['grossSalaryDecimal']}', '{data['salaryTerm']}'"

        self.bankingInfo = f"'{self.firstPageData['NRIC']}', '{data['bankName']}', '{data['bankAccountNumber']}', '{data['typeOfAccount'] if data['typeOfAccount'] != 'other' else data['typeOfAccountOther']}', './pdfFiles/{self.firstPageData['NRIC']}.zip' , '{data['bestContactTime']}', '{data['motorLicense']}', '{data['licenseType'] if data['motorLicense'] == 'hasLicense' else 'None'}', '{data['howToKnowMotosing']}'"

app = MyApp(__name__)
if __name__ == '__main__':
    app.run(host='0.0.0.0')
    """ app.run(root_path=os.path.dirname(os.path.abspath(__file__))) """
