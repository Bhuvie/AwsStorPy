# -*- coding: utf-8 -*-
"""
Created on Wed Feb 01 12:05:34 2017

@author: Bhuvanesh Rajakarthikeyan ID:0051
"""

import os
import boto3
import uuid
from flask import Flask, render_template, request
from flask import make_response,redirect,url_for


PORT = int(os.getenv('PORT', 8080))

app = Flask(__name__)
app.secret_key = 'somesecret'
   
s3client = boto3.resource('s3',aws_access_key_id="*****************",aws_secret_access_key="************************")


@app.route("/")
def start():
    return render_template('login.html') 

@app.route("/index")
def index():
    return render_template('index.html')

@app.route("/loginpage")
def loginpage():
    return render_template('login.html')

@app.route("/registerpag")
def registerpag():
    return render_template('register.html')

@app.route("/registerpage",methods=['POST'])
def registerpage():
    resp = make_response(redirect(url_for('registerpag')))
    return resp

@app.route("/register",methods=['POST'])
def register():
    user=request.form['un']
    passwd=request.form['pwd']
    userstr=user+'_'+passwd
    resp = make_response(redirect(url_for('loginpage')))
    file_name = "users.txt"
    accessglobal('users0051')
    bucket=s3client.Bucket(bucketname)
    for obj in bucket.objects.all():
       if(file_name == obj.key):
           body=obj.get()['Body'].read()
           body=body+" "+userstr
           s3client.Bucket(bucketname).put_object(Key=file_name, Body=body)
           s3client.create_bucket(Bucket=user+"020993")                     #Add random number to bucket name for Unique Bucket name
    return resp        
    

@app.route('/login', methods=['POST'])
def login():
   user = request.form['usrname']
   passwd=request.form['passwd']
   userstr=user+'_'+passwd
   file_name = "users.txt"
   accessglobal('users0051')
   bucket=s3client.Bucket(bucketname)
   for obj in bucket.objects.all():
       if(file_name == obj.key):
           body=obj.get()['Body'].read()
           checkusers=body.split(" ")
           if userstr in checkusers:
               resp = make_response(redirect(url_for('index')))
               resp.set_cookie('userid', user)
               resp.set_cookie('bname',user+"020993")
               accessglobal(user+"020993")
               return resp      
           else:
               return render_template('login.html',error="Invalid Login credentials")
            
   
   

@app.route('/getcookie',methods=['POST'])
def getcookie():
   name = request.cookies.get('userid')
   bname = request.cookies.get('bname')
   return '<h4>Welcome '+name+'. Your S3 Bucket: '+bname+'</h4>'


@app.route('/upload', methods=['POST'])
def upload():
    file1 = request.files['file']
    file_name = file1.filename
    #bname=request.cookies.get('bname')
    #bucketname=bname.format(uuid.uuid4())
    uploaded_content = file1.read()
    uploaded_content=uploaded_content.encode("base64")
    s3client.Bucket(bucketname).put_object(Key=file_name, Body=uploaded_content)
    return "File Successfully Uploaded"
    
@app.route('/download', methods=['POST'])
def download():
    file_name = request.form['dfilename']
    #bname=request.cookies.get('bname')
    #bucketname=bname.format(uuid.uuid4())
    bucket=s3client.Bucket(bucketname)
    for obj in bucket.objects.all():
        if(file_name == obj.key):
            body=obj.get()['Body'].read()
            body=body.decode("base64")
            response = make_response(body)                                                      #If version and name matches return the file as response
            response.headers["Content-Disposition"] = "attachment; filename=%s"%file_name
            return response
    return render_template('index.html',error="File not available for download")
    

@app.route('/delete', methods=['POST'])
def delete():
    file_name = request.form['defilename']
    #bname=request.cookies.get('bname')
    #bucketname=bname.format(uuid.uuid4())
    bucket=s3client.Bucket(bucketname)
    for obj in bucket.objects.all():
        if(file_name == obj.key):
            obj.delete()
    return "File Deleted Successfully"
    
@app.route('/listfiles', methods=['POST'])
def listfiles():
    #bucketnamel = request.form['lbucketname']
    #bname=request.cookies.get('bname')
    #bucketname=bname.format(uuid.uuid4())
    bucket1=s3client.Bucket(bucketname)
    response="<div class='row' style="+'"'+"padding-bottom:10px"+'"'+"><h4><div class='col-sm-5'>FileName</div><div class='col-sm-3'>File Size</div><div class='col-sm-4'>LastUpdatedOn</div></h4></div>"
    for obj in bucket1.objects.all():
        response=response+"<div class='row' style="+'"'+"padding-bottom:10px"+'"'+"><div class='col-sm-5'>"+obj.key+"</div><div class='col-sm-3'>"
        response=response+str(obj.size)+"</div><div class='col-sm-4'>"
        response=response+obj.last_modified.strftime('%Y-%m-%d %H:%M:%S')+"</div></div>"
        #response=response+doc["filehash"]+"</div></div>"
        #<td><textarea rows='3' cols='15'>"
        #response=response+doc["filecontent"]+"</textarea></td></tr>"
    return response
            
def accessglobal(val):
    global bucketname
    bucketname=val.format(uuid.uuid4())          
            

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(PORT))