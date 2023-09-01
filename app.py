from flask import Flask, request, render_template, redirect, url_for, session, make_response
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
import secrets
import time
import subprocess




class MyApp(Flask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config['UPLOAD_FOLDER'] = 'webform'
        self.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
        # self.secondPageData = {}  # Dict that storing first page info
        # self.thirdPageData = {}  # Dict that storing second page info
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
        self.add_url_rule('/reuploadPage', view_func=self.reuploadPage)
        self.add_url_rule('/submitSecondPage', view_func=self.submitSecondPage,
                          methods=['POST'])  # Bind self.submitSecondPage to /submitSecondPage
        self.add_url_rule('/submit', view_func=self.submit,
                          methods=['POST'])  # Bind self.submit to /submit
        self.add_url_rule('/uploadFiles', view_func=self.uploadFiles,
                          methods=['POST']) # Bind self.uploadFiles tp /uploadFiles
        self.add_url_rule('/uploadChunk', view_func=self.uploadChunkedPDF,
                          methods=['POST'])
        self.add_url_rule('/reuploadFiles', view_func=self.reuploadFiles,
                          methods=['POST'])



    # Main Page
    def index(self):
        return render_template('Page1.html')


    # Second page
    def page2(self):
        return render_template('Page2.html')
    

    def page3(self):
        return render_template('Page3.html')
    

    def reuploadPage(self):
        return render_template('Reupload.html')
    

    def reuploadFiles(self):
        nric = request.form['nric']
        self.photos.clear()
        try:
            # merge all files together by simulating a normal upload file
            self.uploadFiles()
            mergedFilename = session['unique_filename']
            # get the file path of saved merged.pdf
            pdfFile = os.path.join(self.config['UPLOAD_FOLDER'], mergedFilename)
            
            # save the merged pdf into a zip
            zipFilePath = f"{nric}.zip"
            
            # list of zip files
            zipFiles = [file for file in os.listdir(self.config['UPLOAD_FOLDER']) if file == zipFilePath]
            
            # check if existing zip file, if not return no nric
            if zipFilePath not in zipFiles:
                print("Wrong NRIC",flush=True)
                return 'NO NRIC'
            
            with zipfile.ZipFile(os.path.join(self.config['UPLOAD_FOLDER'], zipFilePath), 'w') as zf:
                zf.write(pdfFile, f"{nric}.pdf")

            # remove merged pdf
            os.remove(pdfFile)
            
            print("Files has been updated",flush=True)
            return make_response("Success",200)
        except Exception as e:
            print("Files update failed",flush=True)
            traceback.print_exc()
            print(e,flush=True)
    
    



    def uploadChunkedPDF(self):
        try:
            print("Uploading Chunked PDF",flush=True)
            file = request.files['files']
            chunk_number = int(request.form['chunk_number'])
            total_chunks = int(request.form['total_chunks'])
            print(total_chunks)
            filename = file.filename.split('.part')[0]
            chunk_filename = f'{filename}.part{chunk_number}'
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], chunk_filename))
                
            if 'uploaded_filenames' not in session:
                session['uploaded_filenames'] = []   
                
            if chunk_number == total_chunks - 1:
                # All chunks uploaded, merge them into the original file
                merged_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                with open(merged_filename, 'ab') as merged_file:
                    for i in range(total_chunks):
                        chunk_filename = f'{filename}.part{i}'
                        with open(os.path.join(app.config['UPLOAD_FOLDER'], chunk_filename), 'rb') as chunk_file:
                            merged_file.write(chunk_file.read())
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], chunk_filename))
                
                # when all chunks have been merged, the session will append the filename for later usage
                session['uploaded_filenames'].append(filename)
                session.modified = True
                print(f"Appended {filename}",flush=True)
                
                print("Finish Uploading PDF",flush=True)
                return {'message': 'File uploaded and merged successfully'}
            
            print("Successfully Uploaded Chunked PDF",flush=True)
            return {'message': 'File uploaded and merged successfully'}
        except Exception as e:
            print(e,flush=True)
            return {'error'}






    # upload files POST from page 1 
    # Submit button for page 1
    def uploadFiles(self):
        try:
            # will not save in server yet, will just be in array
            print("Merging Files . . .", flush =True)
                 
            if "photo" not in request.files:
                print("No photo found",flush=True)
            else:
                # assign to array
                self.photos.clear()
                self.photos = request.files.getlist('photo')
            
            pdfFiles = session.get('uploaded_filenames','empty')
            
            if pdfFiles == 'empty':
                print("No PDF Files uploaded",flush=True)
                
            # call the process files function to save the files into local
            self.processFiles()
            
            print("Submitted files", flush=True)
            return redirect(url_for('page2'))
        except Exception as e:
            print(e, flush=True)
    
    




    # Submit First Page Handler
    def submitSecondPage(self):
        try:
            session['secondPageData'] = dict(request.form)
            print("SESSION SECOND PAGE DATA --",session['secondPageData'], flush=True)
            print("Submitted second page", flush=True)
            return redirect(url_for('page3'))
        except Exception as e:
            print(e, flush=True)



    # Submit Second Page Handler
    def submit(self):
        print("Submitting form. . .", flush=True)
        try:
            session['thirdPageData'] = dict(request.form)
            self.restructureData()

            flag1 = flag2 = flag3 = flag4 = flag5 = flag6 = False
        except Exception as e:
            print("Error before sql statements", flush=True)
            print(e,flush=True)
            return f"<h1>{e}<h1>"
        
        # check if the database is timed out
        try:
            print("Pinging the server...",flush=True)
            self.db.ping(reconnect=True)
        except mysql.connector.Error:
            print("Connection Timed out",flush=True) 
            
        try:
            query = f"INSERT INTO `Personal Info` (`NRIC`, `Name`, `Phone Number`, `Email`, `Title`, `Gender`, `Race`, `Marital Status`, `Bumi`, `Address`, `No of year in residence`, `Ownership Status`, `Stay in registered address`, `Where user stay(If not stay in registered address)`, `Loan Status`,  `Timestamp`) VALUES ({self.personalInfo})"
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
            query2 = f"INSERT INTO `Working Info` (`NRIC`, `Employment Status`, `Sector`,`Status`, `Position`, `Department`, `Business Nature`, `Company Name`, `Company Phone Number`, `Working in Singapore`, `Company Address`, `When user joined company`,`Net Salary` , `Gross Salary`, `Have EPF`, `Salary Term`) VALUES ({self.workingInfo})"
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

                # Execute SFTP Script to transfer PDF Files
                try: 
                    self.createZipFile()
                    subprocess_args = ['python3', 'scripts/transfer_file_via_sftp.py', f"{session['secondPageData']['NRIC']}.zip"]
                    subprocess.run(subprocess_args, check=True)
                    print("SFTP Transfer completed", flush=True)
                except subprocess.CalledProcessError as e:
                    self.db.rollback()
                    error_message = f"SFTP script execution failed: {e}"
                    print(error_message, flush=True)

                
            except Exception as e:
                self.db.rollback()
                print(e, flush=True)
                return f"<h1>{e}<h1>"
        else:
            self.db.rollback()
            print("Flag detected, not committing to database", flush=True)
            return '<h1>Something is wrong with the data</h1>'

        # reset session data
        session.clear()
        return '<h1>Submitted successfully</h1>'
        





    def processFiles(self):
        try:
            # get files
            photos = self.photos
            pdfFiles = session.get('uploaded_filenames',[])
                
            # save and append the files to merger
            merger = PdfMerger()
            # print("PDFFILES = ", pdfFiles, flush=True)
            
            if len(pdfFiles) > 0:
                for file in pdfFiles:
                    file = os.path.join(self.config['UPLOAD_FOLDER'], file)
                    merger.append(file)

            # merge the image file if there is any
            if len(photos) > 0:
                for photo in photos:
                    image = Image.open(photo.stream)
                    # image = image.resize((1200, 1200))
                
                    # create and write into pdf file
                    pdf_bytes = io.BytesIO()
                    image.save(pdf_bytes, format='PDF')
                    pdf_bytes.seek(0)
                    
                    # append the pdf file of the image into merger
                    merger.append(pdf_bytes)
                    image.close()
            
            # generate unique name for the merged pdf based on timestamp
            # save unique name as a session for later usage
            uniqueName = f"{int(time.time())}_merged.pdf"
            session['unique_filename'] = uniqueName
            
            # write the merged files into a new pdf
            mergedPdfPath = os.path.join(self.config['UPLOAD_FOLDER'],uniqueName)
            with open(mergedPdfPath, 'wb') as combined_pdf_file:
                merger.write(combined_pdf_file)    
            
            # remove saved files
            if len(pdfFiles) > 0:
                for file in pdfFiles:
                    os.remove(os.path.join(self.config['UPLOAD_FOLDER'],file))
            
            # reset the photos
            self.photos.clear()
            
            print("Merged PDF file has been created",flush=True)
        except Exception as e:
            print("Process Files Failed",flush=True)
            traceback.print_exc()
            print(e,flush=True)
            





    def createZipFile(self):
        try:
            uniqueFile = session['unique_filename']
            # get the file path of saved merged.pdf
            pdfFile = os.path.join(self.config['UPLOAD_FOLDER'], uniqueFile)
            
            # save the merged pdf into a zip
            zipFilePath = os.path.join(self.config['UPLOAD_FOLDER'], f"{session['secondPageData']['NRIC']}.zip")
            with zipfile.ZipFile(zipFilePath, 'w') as zf:
                zf.write(pdfFile, f"{session['secondPageData']['NRIC']}.pdf")

            # remove merged pdf
            os.remove(pdfFile)
            print("Zip file has been created",flush=True)

        except Exception as e:
            print("Zip File Creation Failed",flush=True)
            traceback.print_exc()
            print(e,flush=True)
            





    # Restructure all data when submit
    # Gets data from session
    def restructureData(self):
        try:
            data = session['secondPageData']
            print("DEBUGGING SECOND PAGE DATA : ",data,flush=True)
            
            data['gender'] = 'Male'
            if int( data['NRIC']) % 2 == 0:
                data['gender'] = 'Female'
            
            # use array to store all address parts
            addressParts = [data['lot'], data['street']]
            
            # if building name has characters, add it into the array
            if (data.get('buildingName','')):
                addressParts.append(data['buildingName'])
            # if district has characters, add it into the array
            if (data.get('district','')):
                addressParts.append(data['district'])
            # getting city
            city = data.get('citySelect', data['city'])
            # append all the last addresses
            addressParts.extend([data['postcode'], city, data['state']])
            # form an address using join with comma
            address = ', '.join(addressParts)
            address = address.replace("'"," ")
            print("address :", address,flush=True)
            now = datetime.now()
            currentTime = now.strftime("%Y-%m-%d %H:%M:%S")
            
            self.personalInfo = f'"{data["NRIC"]}", "{data["name"]}", "{data["countryCode"] + data["phoneNumber"]}", "{data["email"]}", "{data["title"]}", "{data["gender"]}", "{data["race"] if data["race"] != "" else data["otherRace"]}", "{data["maritalStatus"]}", "{data["bumiornon"]}", "{address}", "{data["numOfYear"]}", "{data["ownership"]}", "{data["stayRegisterAddress"]}", "{data["noStayRegisterAddress"] if data["stayRegisterAddress"] == "No" else "None"}", "NULL", "{currentTime}"'
            
            self.productInfo = f"'{data['NRIC']}', '{data['productType'].lower()}{data['newusedrecon'].lower()}', '{data['brand']}', '{data['modal']}', '{data['usedNumberPlate'] if data['newusedrecon'] == 'Used' else data['reconNumberPlate'] if data['newusedrecon'] == 'Recon' else 'None'}', '{data['tenure']}'"

            referenceContact1 = f"'{data['NRIC']}', '{data['referenceName1']}', '{data['referenceNric1']}', '{data['referenceCountryCode1'] + data['referencePhoneNum1']}', '{data['stayWithReference1']}', '{data['notStayWithApplicant1'] if data['stayWithReference1'] == 'No' else 'None'}', '{data['referenceRelation1']}'"

            referenceContact2 = f"'{data['NRIC']}', '{data['referenceName2']}', '{data.get('referenceNric2','-')}','{data['referenceCountryCode2'] + data['referencePhoneNum2']}', '{data['stayWithReference2']}', '{data['notStayWithApplicant2'] if data['stayWithReference2'] == 'No' else 'None'}', '{data['referenceRelation2']}'"

            self.referenceContacts.clear()
            self.referenceContacts.append(referenceContact1)
            self.referenceContacts.append(referenceContact2)
            print("Finish Restructure second Page Info", flush=True)
        except Exception as e:
            print("Error in Restructure second Page Info", flush=True)
            print(e, flush=True)
            #return f"<h1>{e}<h1>"
            pass
        
        try: 
            data = session['thirdPageData']
            print("DEBUGGING THIRD PAGE DATA : ",data,flush=True)
            employmentStatus = data['employmentStatus']
            status = ''
            if employmentStatus == 'employed':
                status = data['NemployedStatus']
            elif employmentStatus == 'self-employed' and data.get('selfEmployedStatus','') != 'other':
                status = data['selfEmployedStatus']
            #elif employmentStatus == 'retiree':
            #    #need further information
            #    status = ''
            else:
                status = data['selfEmployedOther']

            #let sector be none if employment status is internation or ngo    
            if status in ['international','non-profit organization']:                
                sector = "None"      
            else:
                sector = data['SectorRadio']
            print("Sector Value: ",sector,flush=True)

            #getting detail position
            position = data.get('position','')
            if position == 'operational worker':
                position += '(' + data['PositionSubDropdown'] + ')'
            
            print("Position: ",position,flush=True)

            #getting detail Business Nature
            businessNature = data.get('businessNature','')
            if businessNature in ['foresty','fishing','agriculture','mining','intellectual property','cultural and artistic leadership','other']:
                print("No subBusinessNature")
            else:    
                businessNature += '(' + data['subBusinessNature'] + ')'
            print("BusinessNature: ",businessNature,flush=True)

            #salary part
            netDecimal = data['netSalaryDecimal']
            grossDecimal = data['grossSalaryDecimal']
            
            if not netDecimal:
                netDecimal = "00"
            if not grossDecimal:
                grossDecimal = "00"
            
            # use array to store all address parts
            companyAddressParts = [data['companyLot'], data['companyStreet']]
            
            # if building name has characters, add it into the array
            if (data.get('companyBuildingName','')):
                companyAddressParts.append(data['companyBuildingName'])
                
            # if district has characters, add it into the array
            if (data.get('companyDistrict','')):
                companyAddressParts.append(data['companyDistrict'])
                
            # getting city
            companyCity = data.get('companyCitySelect', data['companyCity'])
            
            # append all the last addresses
            companyAddressParts.extend([data['companyPostcode'], companyCity, data['companyState']])
            # form an address using join with comma
            companyAddress = ', '.join(companyAddressParts)
            companyAddress = companyAddress.replace("'"," ")
            print("Company Address :", companyAddress,flush=True)
            self.workingInfo = f"'{session['secondPageData']['NRIC']}', '{data['employmentStatus']}', '{sector}','{status}', '{position}' , '{data['department']}', '{businessNature}', '{data['companyName']}', '{data['companyCountryCode'] + data['companyPhoneNumber']}', '{data['workinginsingapore']}', '{companyAddress}', '{data['whenJoinedCompany']}', 'RM {data['netSalary'] + '.' + netDecimal}', 'RM {data['grossSalary'] + '.' + grossDecimal}', '{data.get('epfGross','No')}', '{data['salaryTerm']}'"

            self.bankingInfo = f"'{session['secondPageData']['NRIC']}', '{data['bankName']}', '{data['bankAccountNumber']}', '{data['typeOfAccount'] if data['typeOfAccount'] != 'other' else data['typeOfAccountOther']}', './pdfFiles/{session['secondPageData']['NRIC']}.zip'"

            self.extraInfo = f"'{session['secondPageData']['NRIC']}', '{data['bestContactTime']}', '{data['motorLicense']}', '{data['licenseType'] if data['motorLicense'] == 'Yes' else 'None'}', '{data['howToKnowMotosing']}'"
            print("Finish Restructure Third Page Info", flush=True)
        except Exception as e:
            print("Error in Restructure Third Page Info", flush=True)
            print(e, flush = True)
            return f"<h1>{e}<h1>"
        





app = MyApp(__name__)
# for session
app.secret_key = secrets.token_hex(32)
if __name__ == '__main__':
    app.run(host='0.0.0.0')
#EOF
