from flask import Flask, request, render_template, redirect, url_for, session, make_response, jsonify
from PIL import Image
from PyPDF2 import PdfMerger
import PyPDF2
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
import pandas as pd




class MyApp(Flask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config['UPLOAD_FOLDER'] = 'webform'
        self.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
        # self.secondPageData = {}  # Dict that storing first page info
        # self.thirdPageData = {}  # Dict that storing second page info
        self.db = mysql.connector.connect(host='149.28.139.83', user='sharedAccount', password='Shared536442.', database='crm_002_db', port='3306')  # Connect to database
        self.cursor = self.db.cursor()
        # all data are tuples for sql parametize query
        self.personalInfo = ()  # Storing personal info
        self.productInfo = () # Storing product info
        self.referenceContacts = [()]  # A list of reference contacts
        self.workingInfo = ()  # Storing working info
        self.bankingInfo = ()  # Storing bank info
        self.extraInfo = () # Storing extra info
        # self.photos = [] # Array that stores the photos
        # self.pdfFiles = [] # Array that stores the pdfFiles
        self.add_url_rule('/', view_func=self.index,
                          methods=['GET', 'POST'])  # Bind self.index to /
        self.add_url_rule('/privacypolicy', view_func=self.privacypolicy, endpoint='privacypolicy')
        self.add_url_rule('/page1', view_func=self.page1)
        self.add_url_rule('/page2', view_func=self.page2)
        self.add_url_rule('/page3', view_func=self.page3)
        self.add_url_rule('/reuploadPage', view_func=self.reuploadPage)
        self.add_url_rule('/submitPage1Data', view_func=self.submitPage1Data,
                          methods=['POST'])  # Bind self.submitPage1Data to /submitPage1Data
        self.add_url_rule('/submitPage2Data', view_func=self.submitPage2Data,
                          methods=['POST'])
        self.add_url_rule('/submit', view_func=self.submit,
                          methods=['POST'])  # Bind self.submit to /submit
        self.add_url_rule('/uploadFiles', view_func=self.uploadFiles,
                          methods=['POST']) # Bind self.uploadFiles tp /uploadFiles
        self.add_url_rule('/uploadChunk', view_func=self.uploadChunkedPDF,
                          methods=['POST'])
        self.add_url_rule('/reuploadFiles', view_func=self.reuploadFiles,
                          methods=['POST'])
        self.add_url_rule('/postcodeCheck',view_func=self.postcodeCheck,
                          methods=['POST'])
        self.add_url_rule('/authenticate',view_func=self.authenticate,
                          methods=['POST'])
        
    # Main Page
    def index(self):
        session['progress'] = 0
        return render_template('Instructions.html')

    def privacypolicy(self):
        return render_template('PrivacyPolicy.html')
    
    def page1(self):
        authentication = session.get('authenticate',None)
        if authentication:
            session['progress'] = 1
            return render_template('Page1Data.html')
        else:
            print("Invalid Authentication. Redirecting to Index",flush=True)
            return redirect(url_for('index'))
    
    def page2(self):
        sessionProgress = session.get('progress',0)
        authentication = session.get('authenticate',None)
        if sessionProgress == 0 or authentication == None:
            print("Invalid Authentication and Progress. Redirecting to Index",flush=True)
            return redirect(url_for('index'))
        elif (sessionProgress == 1 or sessionProgress == 3)  and authentication:
            session['progress'] = 2
            return render_template('Page2Data.html')
        else:
            return redirect(url_for('index'))
    
    def page3(self):
        sessionProgress = session.get('progress',0)
        authentication = session.get('authenticate',None)
        if sessionProgress == 0 or authentication == None:
            print("Invalid Authentication and Progress. Redirecting to Index",flush=True)
            return redirect(url_for('index'))
        elif sessionProgress == 2 and authentication:
            session['progress'] = 3
            return render_template('pdfUpload.html')
        else: 
            return redirect(url_for('index'))

    def reuploadPage(self):
        return render_template('pdfReupload.html')

    # used in the instruction page to check for captcha token
    # if exist, sign this user as authenticated
    # to allow access to all other routes
    def authenticate(self):
        captcha = request.json.get('captcha',None)
        # print("Captcha Response: ",captcha, flush=True)
        if captcha:
            session['captcha'] = captcha
            session['authenticate'] = "Authenticated"
            return make_response('authenticated',200)
        else:
            return make_response('failed to authenticate',400)
     
    # used to remove empty pdfs
    def removeEmptyPDF(self):
        try:
            pdfFiles = [file for file in os.listdir(self.config['UPLOAD_FOLDER']) if file.endswith('.pdf')]
            for file in pdfFiles:
                filePath = os.path.join(self.config['UPLOAD_FOLDER'], file)
                try:
                    fileSize = os.path.getsize(filePath)
                    # for corrupted files
                    if fileSize == 0:
                        os.remove(filePath)
                        print(f"Removed {filePath}", flush=True)
                    else:
                        # for empty merged.pdf
                        with open(filePath, 'rb') as pdfFile:
                            pdfReader = PyPDF2.PdfReader(pdfFile)
                            if len(pdfReader.pages) == 0:
                                os.remove(filePath)
                                print(f"Removed {filePath}", flush=True)   
                except FileNotFoundError:
                    print("File not found:",filePath, flush=True)
                    
        except Exception as e:
            print(e, flush=True)
    
    
    
    # remove merge pdf if there is error during submission
    def removeMergedPDF(self):
        try:
            mergedPDF = session.get('unique_filename','empty')
            if mergedPDF != 'empty':
                os.remove(os.path.join(self.config['UPLOAD_FOLDER'],mergedPDF))
                print("Removed : ", mergedPDF, flush=True)
        except FileNotFoundError:
            pass
    
    
    
    # reupload file POST endpoint
    def reuploadFiles(self):
        nric = request.form['nric']
        
        print("Reupload NRIC:",nric, flush=True)
        
        # check if existing nric in database, if existing return no nric
        sqlQuery ="SELECT NRIC FROM `Personal Info` WHERE NRIC = %s"
        try:
            queryData = (nric,)
            # check if the database is timed out
            self.db.ping(reconnect=True)
            self.cursor.execute(sqlQuery,queryData)
            data = self.cursor.fetchall()
            if not data:
                print("No NRIC Exist",flush=True)
                return 'NO NRIC',400
        except mysql.connector.Error:
            print("Connection Timed out",flush=True) 
            
        try:
            # merge all files together by simulating a normal upload file
            # will not save in server yet, will just be in array
            print("Merging Files . . .", flush =True)
                 
            if "photo" not in request.files:
                print("No photo found",flush=True)
            else:
                # assign to session
                session['photo'] = request.files.getlist('photo')
            
            pdfFiles = session.get('uploaded_filenames','empty')
            
            if pdfFiles == 'empty':
                print("No PDF Files uploaded",flush=True)
                
            # call the process files function to save the files into local
            self.processFiles()
            
            mergedFilename = session['unique_filename']
            # get the file path of saved merged.pdf
            pdfFile = os.path.join(self.config['UPLOAD_FOLDER'], mergedFilename)
            
            # save the merged pdf into a zip
            zipFilePath = f"{nric}.zip"
              
            # remove original zip file, and create another one
            os.remove(os.path.join(self.config['UPLOAD_FOLDER'],f"{nric}.zip"))
            with zipfile.ZipFile(os.path.join(self.config['UPLOAD_FOLDER'], zipFilePath), 'w') as zf:
                zf.write(pdfFile, f"{nric}.pdf")
            
            # Execute SFTP Script to transfer zip files
            try: 
                subprocess_args = ['python3', 'scripts/transfer_file_via_sftp.py', f"{nric}.zip"]
                subprocess.run(subprocess_args, check=True)
                print("SFTP Transfer completed", flush=True)
            except subprocess.CalledProcessError as e:
                error_message = f"SFTP script execution failed: {e}"
                print(error_message, flush=True)
                
            # remove merged pdf File
            os.remove(pdfFile)
            
            print("Files has been updated",flush=True)
            # reset session data
            session.clear()
            return make_response("Success Reuploading",200)
        except Exception as e:
            print("Files update failed",flush=True)
            session.clear()
            traceback.print_exc()
            print(e,flush=True)
            self.removeEmptyPDF()
            return make_response("Failed Reuploading",500)

    # after submit success, clear all data to prevent possible resubmit
    def clearData(self):
        self.personalInfo = ()
        self.productInfo = ()
        self.referenceContacts = [()]  
        self.workingInfo = () 
        self.bankingInfo = ()
        self.extraInfo = () 
    
    # will be called multiple times to upload all chunks of a pdf file and combined into complete pdf file
    # after uploading all pdf, will call uploadFiles to complete the merge file
    def uploadChunkedPDF(self):
        try:
            print("Uploading Chunked PDF",flush=True)
            file = request.files['files']
            chunk_number = int(request.form['chunk_number'])
            total_chunks = int(request.form['total_chunks'])
            print("Total Chunks :",total_chunks, flush=True)
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
                            
                        try:
                            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], chunk_filename))
                        except FileNotFoundError:
                            pass
                
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
    # Submit button for page 3
    def uploadFiles(self):
        try:
            print("Merging Files . . .", flush =True)
                 
            if "photo" not in request.files:
                print("No photo found",flush=True)
            else:
                # assign to session
                session['photo'] = request.files.getlist('photo')
            
            pdfFiles = session.get('uploaded_filenames','empty')
            
            if pdfFiles == 'empty':
                print("No PDF Files uploaded",flush=True)
                
            # call the process files function to save the files into local
            self.processFiles()
            
            print("Submitted files", flush=True)
            return make_response('upload success',200)
        except Exception as e:
            print(e, flush=True)
            self.removeEmptyPDF()
            return make_response('upload failed',500)
    

    # called during uploadFiles to process images, save as pdf, merging all pdf together
    # generate unique merged pdf file, the unique is based on current time
    # and will be saved in session for further usage
    def processFiles(self):
        try:
            # get files
            photos = session.get('photo', [])
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
                
            try:
                # remove saved files
                if len(pdfFiles) > 0:
                    for file in pdfFiles:
                        os.remove(os.path.join(self.config['UPLOAD_FOLDER'],file))
            except FileNotFoundError:
                pass
            
            # reset the photos and pdf files (if there is, else return none)
            session.pop('photo', None)
            session.pop('uploaded_filenames', None)
            
            print("Merged PDF file has been created",flush=True)
        except Exception as e:
            print("Process Files Failed",flush=True)
            traceback.print_exc()
            print(e,flush=True)



    # to create zip file once it is inside the database 
    # based on the unique merged pdf, create a zip file based on nric
    # and rename the merge pdf file to nric
    def createZipFile(self):
        try:
            uniqueFile = session['unique_filename']
            # get the file path of saved merged.pdf
            pdfFile = os.path.join(self.config['UPLOAD_FOLDER'], uniqueFile)
            
            # save the merged pdf into a zip
            zipFilePath = os.path.join(self.config['UPLOAD_FOLDER'], f"{session['firstPageData']['NRIC']}.zip")
            with zipfile.ZipFile(zipFilePath, 'w') as zf:
                zf.write(pdfFile, f"{session['firstPageData']['NRIC']}.pdf")

            # remove merged pdf
            os.remove(pdfFile)
            print("Zip file has been created",flush=True)

        except Exception as e:
            print("Zip File Creation Failed",flush=True)
            
            traceback.print_exc()
            print(e,flush=True)




    # Submit First Page Handler
    def submitPage1Data(self):
        try:
            session['firstPageData'] = dict(request.form)
            print("SESSION FIRST PAGE DATA --",session['firstPageData'], flush=True)
            print("Submitted first page", flush=True)
            return redirect(url_for('page2'))
        except Exception as e:
            print(e, flush=True)

    # Submit Second Page Handler
    def submitPage2Data(self):
        try:
            session['secondPageData'] = dict(request.form)
            print("SESSION SECOND PAGE DATA --",session['secondPageData'], flush=True)
            print("Submitted second page", flush=True)
            return redirect(url_for('page3'))
        except Exception as e:
            print(e,flush=True)

    # will be called after uploadFiles POST 
    # Submit entire form
    def submit(self):
        print("Submitting form...", flush=True)
        try:
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
            query = "INSERT INTO `Personal Info` (`NRIC`, `Name`, `Phone Number`, `Email`, `Title`, `Gender`, `Race`, `Marital Status`, `Bumi`, `Address`, `No of year in residence`, `Ownership Status`, `Stay in registered address`, `Where user stay(If not stay in registered address)`, `Loan Status`,  `Timestamp`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            self.cursor.execute(query, self.personalInfo)
            print(f"Inserted Personal Info :{self.personalInfo}" , flush=True)
            flag1 = True
        except mysql.connector.Error as e:
            print(f"MySQL Error First Query: {e}", flush=True)
            flag1 = False

        try:
            for i in self.referenceContacts:
                queryX = "INSERT INTO `Reference Contact` (`NRIC`, `Name`,`Reference Contact NRIC`, `Phone Number`, `Stay with user`,`Stay where(If no)`, `Relation to user`) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                self.cursor.execute(queryX, i)
                print(f"Inserted Reference Contact :{i}" , flush=True)
            flag2 = True
        except mysql.connector.Error as e:
            print(f'MySQL Error Second Query: {e}', flush=True)
            flag2 = False

        try:
            query2 = "INSERT INTO `Working Info` (`NRIC`, `Employment Status`, `Sector`,`Status`, `Position`, `Department`, `Business Nature`, `Company Name`, `Company Phone Number`, `Working in Singapore`, `Company Address`, `When user joined company`,`Net Salary` , `Gross Salary`, `Have EPF`, `Salary Term`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            self.cursor.execute(query2, self.workingInfo)
            print(f"Inserted Working Info :{self.workingInfo}" , flush=True)
            flag3 = True
        except mysql.connector.Error as e:
            print(f'MySQL Error Third Query: {e}', flush=True)
            flag3 = False

        try:
            query3 = "INSERT INTO `Banking Info` (`NRIC`, `Bank Name`, `Bank Account Number`, `Type Of Account`, `pdfFilePath`) VALUES (%s, %s, %s, %s, %s)"
            self.cursor.execute(query3, self.bankingInfo)
            print(f"Inserted Banking Info :{self.bankingInfo}" , flush=True)
            flag4 = True
        except mysql.connector.Error as e:
            print(f'Mysql Error Forth Query: {e}', flush=True)
            flag4 = False

        try:
            query4 = "INSERT INTO `Product Info` (`NRIC`, `Product Type`, `Brand`, `Model`, `Number Plate`, `Tenure`) VALUES (%s, %s, %s, %s, %s, %s)"
            self.cursor.execute(query4, self.productInfo)
            print(f"Inserted Product Info :{self.productInfo}" , flush=True)
            flag5 = True
        except mysql.connector.Error as e:
            print(f'Mysql Error Fifth Query: {e}', flush=True)
            flag5 = False

        try:
            query5 = "INSERT INTO `Extra Info` (`NRIC`, `Best time to contact`, `Have license or not`, `License Type`, `How user know Motosing`) VALUES (%s, %s, %s, %s, %s)"
            self.cursor.execute(query5, self.extraInfo)
            print(f"Inserted Extra Info :{self.extraInfo}" , flush=True)
            flag6 = True
        except mysql.connector.Error as e:
            print(f'Mysql Error Sixth Query: {e}', flush=True)
            flag6 = False

        if flag1 and flag2 and flag3 and flag4 and flag5 and flag6:
            try: 
                # insert new row into loan status
                loanStatusQuery = "INSERT INTO `Loan Status` (NRIC) VALUES (%s)"
                self.cursor.execute(loanStatusQuery, (session['firstPageData']['NRIC'],))
                print(f"Inserted Loan Status: {loanStatusQuery}, {session['firstPageData']['NRIC']}", flush=True)

                self.db.commit()
                print("COMMITED INTO DB", flush=True)
                print("Submit complete", flush=True)

                # Execute SFTP Script to transfer PDF Files
                try: 
                    self.createZipFile()
                    subprocess_args = ['python3', 'scripts/transfer_file_via_sftp.py', f"{session['firstPageData']['NRIC']}.zip"]
                    subprocess.run(subprocess_args, check=True)
                    print("SFTP Transfer completed", flush=True)
                except subprocess.CalledProcessError as e:
                    self.db.rollback()
                    error_message = f"SFTP script execution failed: {e}"
                    print(error_message, flush=True)
                    return make_response('sftp error',500)

            except Exception as e:
                self.db.rollback()
                self.removeMergedPDF()
                self.removeEmptyPDF()
                print(e, flush=True)
                return make_response('incorrect data',500)
        else:
            self.db.rollback()
            self.removeMergedPDF()
            self.removeEmptyPDF()
            print("Flag detected, not committing to database", flush=True)
            return make_response('flag detected',500)

        # reset session data and info data
        self.clearData()
        session.clear()
        return make_response('submit success',200)
    
            


    # get postcode from user given
    # check from database then return City and State
    def postcodeCheck(self):
        data = request.json
        postcode = data.get('postcode','')
        try:
            # print("Pinging the server...",flush=True)
            postcode = (postcode,)
            self.db.ping(reconnect=True)
            queryP = "SELECT DISTINCT Area,State FROM `PostcodeMap` WHERE Postcode = %s"
            self.cursor.execute(queryP, postcode)

            location = []
            for row in self.cursor.fetchall():
                location.append({'Area': row[0], 'State': row[1]})

            return jsonify(location)
        except Exception as e:
            return jsonify({'error': str(e)}), 500 


    # Restructure all data when submit
    # Gets data from session
    def restructureData(self):
        try:
            data = session['firstPageData']
            print("DEBUGGING FIRST PAGE DATA : ",data,flush=True)
            
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
            
            # for timestamp
            now = datetime.now()
            currentTime = now.strftime("%Y-%m-%d %H:%M:%S")
            
            self.personalInfo = (data['NRIC'], data["name"], data["countryCode"] + data["phoneNumber"], data["email"], data["title"], data["gender"], data["race"] if data["race"] != "" else data["otherRace"], data["maritalStatus"], data["bumiornon"], address, data["numOfYear"], data["ownership"], data["stayRegisterAddress"], data["noStayRegisterAddress"] if data["stayRegisterAddress"] == "No" else "None", 'NULL', currentTime)
            
            self.productInfo = (data['NRIC'], data['productType'].lower()+data['newusedrecon'].lower(), data['brand'], data['model'], data['usedNumberPlate'] if data['newusedrecon'] == 'Used' else data['reconNumberPlate'] if data['newusedrecon'] == 'Recon' else 'None', data['tenure'])

            referenceContact1 = (data['NRIC'], data['referenceName1'], data['referenceNric1'], data['referenceCountryCode1'] + data['referencePhoneNum1'], data['stayWithReference1'], data['notStayWithApplicant1'] if data['stayWithReference1'] == 'No' else 'None', data['referenceRelation1'])

            referenceContact2 = (data['NRIC'], data['referenceName2'], data.get('referenceNric2','-') ,data['referenceCountryCode2'] + data['referencePhoneNum2'], data['stayWithReference2'], data['notStayWithApplicant2'] if data['stayWithReference2'] == 'No' else 'None', data['referenceRelation2'])

            self.referenceContacts.clear()
            self.referenceContacts.append(referenceContact1)
            self.referenceContacts.append(referenceContact2)
            print("Finish Restructure first Page Info", flush=True)
        except Exception as e:
            print("Error in Restructure first Page Info", flush=True)
            print(e, flush=True)
            pass
        
        try: 
            data = session['secondPageData']
            print("DEBUGGING SECOND PAGE DATA : ",data,flush=True)
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
            
            netSalary = f'RM {data["netSalary"]}.{netDecimal}'
            grossSalary = f'RM {data["grossSalary"]}.{grossDecimal}'
            
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
            
            filePath = f'./pdfFiles/{session["firstPageData"]["NRIC"]}.zip'
            
            self.workingInfo = (session['firstPageData']['NRIC'], data['employmentStatus'], sector, status, position, data['department'], businessNature, data['companyName'], data['companyCountryCode'] + data['companyPhoneNumber'], data['workinginsingapore'], companyAddress, data['whenJoinedCompany'], netSalary, grossSalary, data.get('epfGross','No'), data['salaryTerm'])

            self.bankingInfo = (session['firstPageData']['NRIC'], data['bankName'], data['bankAccountNumber'], data['typeOfAccount'], filePath)

            self.extraInfo = (session['firstPageData']['NRIC'], data['bestContactTime'], data['motorLicense'], data['licenseType'] if data['motorLicense'] == 'Yes' else 'None', data['howToKnowMotosing'])
            print("Finish Restructure Second Page Info", flush=True)
        except Exception as e:
            print("Error in Restructure Second Page Info", flush=True)
            print(e, flush = True)
        
app = MyApp(__name__)
# for session
app.secret_key = secrets.token_hex(32)
if __name__ == '__main__':
    app.run(host='0.0.0.0')
#EOF