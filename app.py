from flask import Flask, request, render_template, redirect, url_for
from reportlab.pdfgen import canvas
from PyPDF2 import PdfMerger
import mysql.connector
import zipfile
import json
import os
from datetime import datetime 

# TODO:UPDATE BUSINESS OF NATURE
# TODO:UPDATE TYPE OF OCCUPATION


class MyApp(Flask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config['UPLOAD_FOLDER'] = './pdfFiles'
        self.firstPageData = {}  # Dict that storing first page info
        self.secondPageData = {}  # Dict that storing second page info
        self.db = mysql.connector.connect(host='149.28.139.83', user='sharedAccount', password='Shared536442.', database='crm_002_db', port='3306')  # Connect to database
        self.cursor = self.db.cursor()
        self.personalInfo = ""  # Storing personal info
        self.productInfo = "" # Storing product info
        self.referenceContacts = []  # A list of reference contacts
        self.workingInfo = ""  # Storing working info
        self.bankingInfo = ""  # Storing bank info
        self.extraInfo = "" # Storing extra info
        self.add_url_rule('/', view_func=self.index,
                          methods=['GET', 'POST'])  # Bind self.index to /
        # Bind self.page2 to /page2
        self.add_url_rule('/page2', view_func=self.page2)
        self.add_url_rule('/submitFirstPage', view_func=self.submitFirstPage,
                          methods=['POST'])  # Bind self.submitFirstPage to /submitFirstPage
        self.add_url_rule('/submit', view_func=self.submit,
                          methods=['POST'])  # Bind self.submit to /submit

    # Main Page
    def index(self):
        return render_template('Page1.html')

    # Second page
    def page2(self):
        return render_template('Page2.html')

    # Submit First Page Handler
    def submitFirstPage(self):
        try:
            self.firstPageData = dict(request.form)
            self.firstPageData['gender'] = 'Male'
            if int( self.firstPageData['NRIC']) % 2 == 0:
                self.firstPageData['gender'] = 'Female'
            self.restructureFirstPageInfo()
            print("Submitted first page . . .", flush=True)
            return redirect(url_for('page2'))
        except Exception as e:
            print(e, flush=True)

    # Submit Second Page Handler
    def submit(self):
        print("Submitting form. . .", flush=True)
        try:
        # try:
        #     capturedPhoto = json.loads(request.form.get('capturedPhoto'))

        #     for i, photo_data_uri in enumerate(capturedPhoto):
        #         photo_pdf_path = f"./pdfFiles/photo_{i}.pdf"
        #         c = canvas.Canvas(photo_pdf_path)
        #         c.drawImage(photo_data_uri, 0, 0, 200, 200)
        #         c.save()

        #     pdfFiles.append(open(photo_pdf_path, 'rb'))
        # except Exception as e:
        #     print(e)
        #     pass
            pdfFiles = request.files.getlist('pdfFiles')
            zipFileName = f"./pdfFiles/{self.firstPageData['NRIC']}.zip"
            print("PDF Files", pdfFiles, flush=True)

            merger = PdfMerger()

            for file in pdfFiles:
                # check if the file has any content to avoid merging empty file
                if file.content_length > 0:
                    merger.append(file)

            mergedPdfPath = f"./pdfFiles/{self.firstPageData['NRIC']}.pdf"
            merger.write(mergedPdfPath)
            merger.close()

            with zipfile.ZipFile(zipFileName, 'w') as zf:
                zf.write(mergedPdfPath, f"{self.firstPageData['NRIC']}.pdf")

            os.system('rm -rf ./pdfFiles/*.pdf')

            self.secondPageData = dict(request.form)
            self.restructureSecondPageInfo()

            flag1 = flag2 = flag3 = flag4 = flag5 = flag6 = False
        except Exception as e:
            print("Error before sql statements", flush=True)
            print(e,flush=True)
            return f"<h1>{e}<h1>"
            
        try:
            query = f"INSERT INTO `Personal Info` VALUES ({self.personalInfo})"
            self.cursor.execute(query)
            print(f"Inserted {self.personalInfo}" , flush=True)
            flag1 = True
        except mysql.connector.Error as e:
            print(f"MySQL Error First Query: {e}", flush=True)
            flag1 = False

        try:
            for i in self.referenceContacts:
                queryX = f"INSERT INTO `Reference Contact` (`NRIC`, `Name`,`Reference Contact NRIC`, `Phone Number`, `Stay with user`,`Stay where(If no)`, `Relation to user`) VALUES ({i})"
                self.cursor.execute(queryX)
            flag2 = True
        except mysql.connector.Error as e:
            print(f'MySQL Error Second Query: {e}', flush=True)
            flag2 = False

        try:
            query2 = f"INSERT INTO `Working Info` (`NRIC`, `Employment Status`, `Status`, `Position`, `Department`, `Business Nature`, `Company Name`, `Company Phone Number`, `Working in Singapore`, `Company Address`, `When user joined company`,`Net Salary` , `Gross Salary`, `Have EPF`, `Salary Term`) VALUES ({self.workingInfo})"
            self.cursor.execute(query2)
            flag3 = True
        except mysql.connector.Error as e:
            print(f'MySQL Error Third Query: {e}', flush=True)
            flag3 = False

        try:
            query3 = f"INSERT INTO `Banking Info` (`NRIC`, `Bank Name`, `Bank Account Number`, `Type Of Account`, `pdfFilePath`) VALUES ({self.bankingInfo})"
            self.cursor.execute(query3)
            flag4 = True
        except mysql.connector.Error as e:
            print(f'Mysql Error Forth Query: {e}', flush=True)
            flag4 = False

        try:
            query4 = f"INSERT INTO `Product Info` (`NRIC`, `Product Type`, `Brand`, `Model`, `Number Plate`, `Tenure`) VALUES ({self.productInfo})"
            self.cursor.execute(query4)
            flag5 = True
        except mysql.connector.Error as e:
            print(f'Mysql Error Fifth Query: {e}', flush=True)
            flag5 = False

        try:
            query5 = f"INSERT INTO `Extra Info` (`NRIC`, `Best time to contact`, `Have license or not`, `License Type`, `How user know Motosing`) VALUES ({self.extraInfo})"
            self.cursor.execute(query5)
            flag6 = True
        except mysql.connector.Error as e:
            print(f'Mysql Error Sixth Query: {e}', flush=True)
            flag6 = False

        if flag1 and flag2 and flag3 and flag4 and flag5 and flag6:
            try: 
                self.db.commit()
                print("COMMITED INTO DB", flush=True)
                print("Submit complete", flush=True)
            except Exception as e:
                print(e, flush=True)
                return f"<h1>{e}<h1>"
        else:
            print("Flag detected, not committing to database", flush=True)

        return '<h1>Submitted, please wait</h1>'

    # Restructure First Page Data into a string
    def restructureFirstPageInfo(self):
        try:
            data = self.firstPageData
            
            now = datetime.now()
            currentTime = now.strftime("%Y-%m-%d %H:%M:%S")
            
            self.personalInfo = f"'{data['NRIC']}', '{data['name']}', '{data['countryCode'] + data['phoneNumber']}', '{data['email']}', '{data['title']}', '{data['gender']}', '{data['race'] if data['race'] != '' else data['otherRace']}', '{data['maritalStatus']}', '{data['bumiornon']}', '{data['address']}', '{data['numOfYear']}', '{data['ownership']}', '{data['stayRegisterAddress']}', '{data['noStayRegisterAddress'] if data['stayRegisterAddress'] == 'No' else 'None'}', '{currentTime}'"
            self.productInfo = f"'{data['NRIC']}', '{data['productType'].lower()}{data['newusedrecon'].lower()}', '{data['brand']}', '{data['modal']}', '{data['usedNumberPlate'] if data['newusedrecon'] == 'Used' else data['reconNumberPlate'] if data['newusedrecon'] == 'Recon' else 'None'}', '{data['tenure']}'"

            referenceContact1 = f"'{data['NRIC']}', '{data['referenceName1']}', '{data['referenceNric1']}', '{data['referenceCountryCode1'] + data['referencePhoneNum1']}', '{data['stayWithReference1']}', '{data['notStayWithApplicant1'] if data['stayWithReference1'] == 'No' else 'None'}', '{data['referenceRelation1']}'"

            referenceContact2 = f"'{data['NRIC']}', '{data['referenceName2']}', '{data['referenceNric2']}','{data['referenceCountryCode2'] + data['referencePhoneNum2']}', '{data['stayWithReference2']}', '{data['notStayWithApplicant2'] if data['stayWithReference2'] == 'No' else 'None'}', '{data['referenceRelation2']}'"

            self.referenceContacts.clear()
            self.referenceContacts.append(referenceContact1)
            self.referenceContacts.append(referenceContact2)
            print("Finish Restructure First Page Info", flush=True)
        except Exception as e:
            print("Error in Restructure First Page Info", flush=True)
            print(e, flush=True)
            return f"<h1>{e}<h1>"

    # Restructure Second Page Data into a string
    def restructureSecondPageInfo(self):
        try: 
            data = self.secondPageData
            employmentStatus = data['employmentStatus']
            status = ''
            if employmentStatus == 'employed':
                status = data['NemployedStatus']
            elif employmentStatus == 'other':
                status = data['selfEmployedOther']
                if status == 'yes':
                    status = data['otherIncomeSourceOther']
            elif employmentStatus == 'student':
                status = 'None'
                data['department'] = "None"
                data['position'] = "None"
                
            elif employmentStatus == 'self-employed' and data.get('selfEmployedStatus','') != 'other':
                status = data['selfEmployedStatus']
            else:
                status = data['selfEmployedOther']
            
            self.workingInfo = f"'{self.firstPageData['NRIC']}', '{data['employmentStatus']}', '{status}', '{data['position']}', '{data['department']}', '{data['businessNature']}', '{data['companyName']}', '{data['companyCountryCode'] + data['companyPhoneNumber']}', '{data['workinginsingapore']}', '{data['companyAddress']}', '{data['whenJoinedCompany']}', 'RM {data['netSalary'] + '.' + data['netSalaryDecimal']}', 'RM {data['grossSalary'] + '.' + data['grossSalaryDecimal']}', '{data['efpGross']}', '{data['salaryTerm']}'"

            self.bankingInfo = f"'{self.firstPageData['NRIC']}', '{data['bankName']}', '{data['bankAccountNumber']}', '{data['typeOfAccount'] if data['typeOfAccount'] != 'other' else data['typeOfAccountOther']}', './pdfFiles/{self.firstPageData['NRIC']}.zip'"

            self.extraInfo = f"'{self.firstPageData['NRIC']}', '{data['bestContactTime']}', '{data['motorLicense']}', '{data['licenseType'] if data['motorLicense'] == 'Yes' else 'None'}', '{data['howToKnowMotosing']}'"
            print("Finish Restructure Second Page Info", flush=True)
        except Exception as e:
            print("Error in Restructure Second Page Info", flush=True)
            print(e, flush = True)
            return f"<h1>{e}<h1>"

app = MyApp(__name__)
if __name__ == '__main__':
    app.run(host='0.0.0.0')
#EOF
