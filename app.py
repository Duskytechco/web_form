from flask import Flask, request, render_template, redirect, url_for
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
from PyPDF2 import PdfMerger
import mysql.connector
import zipfile
import json
import io
import os
from datetime import datetime 
import traceback


# TODO:UPDATE BUSINESS OF NATURE
# TODO:UPDATE TYPE OF OCCUPATION


class MyApp(Flask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config['UPLOAD_FOLDER'] = 'webform'
        self.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
        self.secondPageData = {}  # Dict that storing first page info
        self.thirdPageData = {}  # Dict that storing second page info
        self.db = mysql.connector.connect(host='149.28.139.83', user='sharedAccount', password='Shared536442.', database='crm_002_db', port='3306')  # Connect to database
        self.cursor = self.db.cursor()
        self.personalInfo = ""  # Storing personal info
        self.productInfo = "" # Storing product info
        self.referenceContacts = []  # A list of reference contacts
        self.workingInfo = ""  # Storing working info
        self.bankingInfo = ""  # Storing bank info
        self.extraInfo = "" # Storing extra info
        self.photos = [] # Array that stores the photos
        self.pdfFiles = [] # Array that stores the pdfFiles
        self.add_url_rule('/', view_func=self.index,
                          methods=['GET', 'POST'])  # Bind self.index to /
        # Bind self.page2 to /page2
        self.add_url_rule('/page2', view_func=self.page2)
        self.add_url_rule('/page3', view_func=self.page3)
        self.add_url_rule('/submitSecondPage', view_func=self.submitSecondPage,
                          methods=['POST'])  # Bind self.submitSecondPage to /submitSecondPage
        self.add_url_rule('/submit', view_func=self.submit,
                          methods=['POST'])  # Bind self.submit to /submit
        self.add_url_rule('/uploadFiles', view_func=self.uploadFiles,
                          methods=['POST']) # Bind self.uploadFiles tp /uploadFiles
        # self.add_url_rule('/uploadChunkFiles', view_func=self.uploadChunkedPDF,
        #                   methods=['POST'])

    # Main Page
    def index(self):
        return render_template('Page1.html')

    # Second page
    def page2(self):
        return render_template('Page2.html')
    
    def page3(self):
        return render_template('Page3.html')
    
    # def uploadChunkedPDF(self):
    #     try:
    #         print("Uploading Chunked PDF",flush=True)
    #         pdfFiles = request.files['files']
    #         print("PDFFiles :",pdfFiles, flush=True)
    #         self.pdfFiles = pdfFiles.filename
    #         for file in pdfFiles:
    #             file.save(os.path.join(self.config['UPLOAD_FOLDER'], file.filename))
                
    #     except Exception as e:
    #         print(e,flush=True)
            
    # upload files POST from page 1 
    # Submit button for page 1
    def uploadFiles(self):
        try:
            # will not save in server yet, will just be in array
            print("Saving Files . . .", flush =True)
            if "pdfFiles" not in request.files:
                print("No PDF Files found", flush=True)
            else:
                # assign to array
                self.pdfFiles.clear()
                self.pdfFiles = request.files.getlist('pdfFiles')
                 
            if "photo" not in request.files:
                print("No photo found",flush=True)
            else:
                # assign to array
                self.photos.clear()
                self.photos = request.files.getlist('photo')
                
            if "pdfFiles" in request.files or "photo" in request.files:
                # call the process files function to save the files into local
                self.processFiles()
                print("Files Saved", flush=True)
            
            print("Submitted first page . . .", flush=True)
            return redirect(url_for('page2'))
        except Exception as e:
            print(e, flush=True)
    
    
    # Submit First Page Handler
    def submitSecondPage(self):
        try:
            self.secondPageData = dict(request.form)
            self.secondPageData['gender'] = 'Male'
            if int( self.secondPageData['NRIC']) % 2 == 0:
                self.secondPageData['gender'] = 'Female'
            self.restructureSecondPageInfo()
            print("Submitted second page . . .", flush=True)
            return redirect(url_for('page3'))
        except Exception as e:
            print(e, flush=True)

    # Submit Second Page Handler
    def submit(self):
        print("Submitting form. . .", flush=True)
        try:
            # create the zip file with the NRIC
            self.createZipFile()
            
            self.thirdPageData = dict(request.form)
            self.restructureThirdPageInfo()

            flag1 = flag2 = flag3 = flag4 = flag5 = flag6 = False
        except Exception as e:
            print("Error before sql statements", flush=True)
            print(e,flush=True)
            return f"<h1>{e}<h1>"
            
        try:
            query = f"INSERT INTO `Personal Info` VALUES ({self.personalInfo})"
            self.cursor.execute(query)
            print(f"Inserted Personal Info :{self.personalInfo}" , flush=True)
            flag1 = True
        except mysql.connector.Error as e:
            print(f"MySQL Error First Query: {e}", flush=True)
            flag1 = False

        try:
            for i in self.referenceContacts:
                queryX = f"INSERT INTO `Reference Contact` (`NRIC`, `Name`,`Reference Contact NRIC`, `Phone Number`, `Stay with user`,`Stay where(If no)`, `Relation to user`) VALUES ({i})"
                self.cursor.execute(queryX)
                print(f"Inserted Reference Contact :{i}" , flush=True)
            flag2 = True
        except mysql.connector.Error as e:
            print(f'MySQL Error Second Query: {e}', flush=True)
            flag2 = False

        try:
            query2 = f"INSERT INTO `Working Info` (`NRIC`, `Employment Status`, `Status`, `Position`, `Department`, `Business Nature`, `Company Name`, `Company Phone Number`, `Working in Singapore`, `Company Address`, `When user joined company`,`Net Salary` , `Gross Salary`, `Have EPF`, `Salary Term`) VALUES ({self.workingInfo})"
            self.cursor.execute(query2)
            print(f"Inserted Working Info :{self.workingInfo}" , flush=True)
            flag3 = True
        except mysql.connector.Error as e:
            print(f'MySQL Error Third Query: {e}', flush=True)
            flag3 = False

        try:
            query3 = f"INSERT INTO `Banking Info` (`NRIC`, `Bank Name`, `Bank Account Number`, `Type Of Account`, `pdfFilePath`) VALUES ({self.bankingInfo})"
            self.cursor.execute(query3)
            print(f"Inserted Banking Info :{self.bankingInfo}" , flush=True)
            flag4 = True
        except mysql.connector.Error as e:
            print(f'Mysql Error Forth Query: {e}', flush=True)
            flag4 = False

        try:
            query4 = f"INSERT INTO `Product Info` (`NRIC`, `Product Type`, `Brand`, `Model`, `Number Plate`, `Tenure`) VALUES ({self.productInfo})"
            self.cursor.execute(query4)
            print(f"Inserted Product Info :{self.productInfo}" , flush=True)
            flag5 = True
        except mysql.connector.Error as e:
            print(f'Mysql Error Fifth Query: {e}', flush=True)
            flag5 = False

        try:
            query5 = f"INSERT INTO `Extra Info` (`NRIC`, `Best time to contact`, `Have license or not`, `License Type`, `How user know Motosing`) VALUES ({self.extraInfo})"
            self.cursor.execute(query5)
            print(f"Inserted Extra Info :{self.extraInfo}" , flush=True)
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
                self.db.rollback()
                print(e, flush=True)
                return f"<h1>{e}<h1>"
        else:
            self.db.rollback()
            print("Flag detected, not committing to database", flush=True)
            return '<h1>Something is wrong with the data</h1>'

        return '<h1>Submitted, please wait</h1>'
        
    def processFiles(self):
        try:
            # get files
            pdfFiles = self.pdfFiles
            photos = self.photos
            
            # save and append the files to merger
            merger = PdfMerger()
            if len(pdfFiles) > 0:
                for file in pdfFiles:
                    # file.save(os.path.join(self.config['UPLOAD_FOLDER'], file.filename))
                    merger.append(file)

            # merge the image file if there is any
            if len(photos) > 0:
                for photo in photos:
                    image = Image.open(photo.stream)
                    image = image.resize((400, 300))
                
                    # create and write into pdf file
                    pdf_bytes = io.BytesIO()
                    image.save(pdf_bytes, format='PDF')
                    pdf_bytes.seek(0)
                    
                    # append the pdf file of the image into merger
                    merger.append(pdf_bytes)
                    image.close()
            
            # write the merged files into a new pdf
            mergedPdfPath = os.path.join(self.config['UPLOAD_FOLDER'],"merged.pdf")
            with open(mergedPdfPath, 'wb') as combined_pdf_file:
                merger.write(combined_pdf_file)    
            
            # remove saved files
            for file in pdfFiles:
                os.remove(os.path.join(self.config['UPLOAD_FOLDER'],file.filename))
            
            print("Merged PDF file has been created",flush=True)
        except Exception as e:
            print("Process Files Failed",flush=True)
            traceback.print_exc()
            print(e,flush=True)
            
    def createZipFile(self):
        try:
            # get the file path of saved merged.pdf
            pdfFile = os.path.join(self.config['UPLOAD_FOLDER'], f"merged.pdf")
            
            # save the merged pdf into a zip
            zipFilePath = os.path.join(self.config['UPLOAD_FOLDER'], f"{self.secondPageData['NRIC']}.zip")
            with zipfile.ZipFile(zipFilePath, 'w') as zf:
                zf.write(pdfFile, f"{self.secondPageData['NRIC']}.pdf")

            # remove merged pdf
            os.remove(pdfFile)
            
            print("Zip file has been created",flush=True)
        except Exception as e:
            print("Zip File Creation Failed",flush=True)
            traceback.print_exc()
            print(e,flush=True)
    
    # Restructure First Page Data into a string
    def restructureSecondPageInfo(self):
        try:
            data = self.secondPageData
            # print("DEBUGGING SECOND PAGE DATA : ",data,flush=True)
            
            now = datetime.now()
            currentTime = now.strftime("%Y-%m-%d %H:%M:%S")
            
            self.personalInfo = f"'{data['NRIC']}', '{data['name']}', '{data['countryCode'] + data['phoneNumber']}', '{data['email']}', '{data['title']}', '{data['gender']}', '{data['race'] if data['race'] != '' else data['otherRace']}', '{data['maritalStatus']}', '{data['bumiornon']}', '{data['address']}', '{data['numOfYear']}', '{data['ownership']}', '{data['stayRegisterAddress']}', '{data['noStayRegisterAddress'] if data['stayRegisterAddress'] == 'No' else 'None'}', '{currentTime}'"
            self.productInfo = f"'{data['NRIC']}', '{data['productType'].lower()}{data['newusedrecon'].lower()}', '{data['brand']}', '{data['modal']}', '{data['usedNumberPlate'] if data['newusedrecon'] == 'Used' else data['reconNumberPlate'] if data['newusedrecon'] == 'Recon' else 'None'}', '{data['tenure']}'"

            referenceContact1 = f"'{data['NRIC']}', '{data['referenceName1']}', '{data['referenceNric1']}', '{data['referenceCountryCode1'] + data['referencePhoneNum1']}', '{data['stayWithReference1']}', '{data['notStayWithApplicant1'] if data['stayWithReference1'] == 'No' else 'None'}', '{data['referenceRelation1']}'"

            referenceContact2 = f"'{data['NRIC']}', '{data['referenceName2']}', '{data['referenceNric2']}','{data['referenceCountryCode2'] + data['referencePhoneNum2']}', '{data['stayWithReference2']}', '{data['notStayWithApplicant2'] if data['stayWithReference2'] == 'No' else 'None'}', '{data['referenceRelation2']}'"

            self.referenceContacts.clear()
            self.referenceContacts.append(referenceContact1)
            self.referenceContacts.append(referenceContact2)
            print("Finish Restructure second Page Info", flush=True)
        except Exception as e:
            print("Error in Restructure second Page Info", flush=True)
            print(e, flush=True)
            return f"<h1>{e}<h1>"

    # Restructure Second Page Data into a string
    def restructureThirdPageInfo(self):
        try: 
            data = self.thirdPageData
            # print("DEBUGGING THIRD PAGE DATA : ",data,flush=True)
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
                
            netDecimal = data['netSalaryDecimal']
            grossDecimal = data['grossSalaryDecimal']
            
            if not netDecimal:
                netDecimal = "00"
            if not grossDecimal:
                grossDecimal = "00"
            
            self.workingInfo = f"'{self.secondPageData['NRIC']}', '{data['employmentStatus']}', '{status}', '{data['position']}', '{data['department']}', '{data['businessNature']}', '{data['companyName']}', '{data['companyCountryCode'] + data['companyPhoneNumber']}', '{data['workinginsingapore']}', '{data['companyAddress']}', '{data['whenJoinedCompany']}', 'RM {data['netSalary'] + '.' + netDecimal}', 'RM {data['grossSalary'] + '.' + grossDecimal}', '{data.get('epfGross','No')}', '{data['salaryTerm']}'"

            self.bankingInfo = f"'{self.secondPageData['NRIC']}', '{data['bankName']}', '{data['bankAccountNumber']}', '{data['typeOfAccount'] if data['typeOfAccount'] != 'other' else data['typeOfAccountOther']}', './pdfFiles/{self.secondPageData['NRIC']}.zip'"

            self.extraInfo = f"'{self.secondPageData['NRIC']}', '{data['bestContactTime']}', '{data['motorLicense']}', '{data['licenseType'] if data['motorLicense'] == 'Yes' else 'None'}', '{data['howToKnowMotosing']}'"
            print("Finish Restructure Third Page Info", flush=True)
        except Exception as e:
            print("Error in Restructure Third Page Info", flush=True)
            print(e, flush = True)
            return f"<h1>{e}<h1>"

app = MyApp(__name__)
if __name__ == '__main__':
    app.run(host='0.0.0.0')
#EOF
