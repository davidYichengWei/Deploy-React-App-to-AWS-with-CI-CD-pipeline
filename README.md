# Deploy-React-App-to-AWS-with-CI-CD-pipeline
This is a step-by-step guide on deploying a React static website to AWS and setting up a CI/CD pipeline.


## Motivation
During the past few months, I was developing a React website for a club at U of T while learning AWS. After getting several AWS Certifications, I thought it would be a good opportunity to practice my AWS skills by deploying the React App to AWS.

I want the deployment to be fully serverless, so that I don't have to manage any server, and with CI/CD pipeline built in, so that any change pushed to main branch in the repository would be automatically deployed to the public website.

While doing research, I found several helpful documentations, but none of them provides detailed end-to-end instructions. The purpose of this project is to fill this gap and to better help people deploy their React website to AWS.


## Prerequisites 
To begin with this project, you need:
- A React App to be hosted
- An AWS account
  - Best practices: don't use the root user of your AWS account to perform daily tasks, create an IAM user instead. See https://docs.aws.amazon.com/IAM/latest/UserGuide/id_root-user.html


## Overview
There are multiple ways you can host a static website on AWS, including S3, Amplify, EC2, etc. For this project, S3 was chosen because it is the easiest to get started with and serverless.

CodeBuild, CodeDeploy were used to build CI/CD pipeline, and CodePipeline was used to orchestrate the process.

Route 53 was used to route a custom domain to the S3 bucket website endpoint.

[Optional] A CloudFront distribution was set up in front of the S3 bucket, so that the content can be cached in edge locations and access to S3 bucket can be restricted to CloudFront distribution with origin access control settings, which enhances security. To ensure that users always get the latest content from CloudFront, S3 Event Notifications were used to trigger a Lambda function whenever the bucket gets updated, to invalidate CloudFront cache.


## 1. Host React Website on S3
Let's forget about the CI/CD pipeline for now and just get our website working by manually upload it to S3.

1. First, create a new bucket in S3 for hosting the website. Uncheck "Block all public access" and leave everything else as default. This will allow people to access your website.
<img width="810" alt="Screenshot 2022-09-02 at 8 41 29 PM" src="https://user-images.githubusercontent.com/77185679/188249144-1d498418-f030-46a0-94f7-897794071b85.png">
<br/><br/>

2. In the bucket, go to Properties and scroll to the buttom to enable "Static website hosting". Set BOTH "Index document" and "Error document" to index.html. It's important to set "Error document" as well, otherwise the application won't be able to route to different paths (e.g. example.com/page1, example.com/page2).
<img width="786" alt="Screenshot 2022-09-02 at 8 47 54 PM" src="https://user-images.githubusercontent.com/77185679/188249291-14574024-9ed0-4728-bbb5-a2e0bbd04ea5.png">
<br/><br/>

3. In the bucket, under Permissions, edit bucket policy and click on "Policy generator".
Apply the following configurations. For Actions, select GetObject. 
<img width="994" alt="Screenshot 2022-09-02 at 9 17 38 PM" src="https://user-images.githubusercontent.com/77185679/188250305-a6c8a520-7b4f-4bd9-a277-ac08fd9089e3.png">
<br/><br/>

4. For ARN, go back to the edit bucket policy page, copy bucket ARN, and enter \<bucket ARN\>/* (e.g. arn:aws:s3:::react-website-hosting-project/*). It's important to add /\* after the bucket ARN, because this policy needs to be applied to all objects within the bucket, not the bucket itself.
<img width="1385" alt="Screenshot 2022-09-02 at 9 18 55 PM" src="https://user-images.githubusercontent.com/77185679/188250333-386fc22a-7664-4342-8f45-1534aa70bbdf.png">
<br/><br/>

5. Then click on Add Statement, Generate Policy, and copy the JSON policy to the edit policy page, save changes.
<img width="844" alt="Screenshot 2022-09-02 at 9 22 53 PM" src="https://user-images.githubusercontent.com/77185679/188250513-a27fb583-e627-4b82-9737-331fddfe3494.png">
<br/><br/>

6. Next, go to your React App. If you don't have a build already, run the following command to create a build, which should create a build folder under the root directory of your project.
   ```
   npm install
   npm run build
   ```

7. In the bucket, to go Objects, upload everything in the build folder to the S3 bucket. (Note: DO NOT upload the build folder as a folder, instead, upload individual files and upload any folder inside build folder as folder).

8. Now, you should be able to access your website by clicking the link under Properties -> Static website hosting -> Bucket website endpoint.
<img width="1286" alt="Screenshot 2022-09-02 at 9 49 48 PM" src="https://user-images.githubusercontent.com/77185679/188251279-e564545a-3376-420e-8552-7786f4aaa977.png">
<br/><br/>


## 2. Set Up CI/CD Pipeline
CI/CD means continuous integration, continuous delivery and continuous deployment. In this project, CodeBuild is used for CI to generate build for the React App, CodeDeploy is used for CD to deploy the build generated to S3, and CodePipeline is used to orchestrate the whole process.

To get started, go to CodePipeline and click "Create pipeline". Choose a pipeline name and allow it to create a new service role for the pipeline. This will give CodePipeline permissions to interact with other services.
<img width="1064" alt="Screenshot 2022-09-03 at 3 03 00 PM" src="https://user-images.githubusercontent.com/77185679/188284645-0ff26bad-5c71-4bc4-aa7b-deb65ac1443f.png">
<br/><br/>

### Source Stage
At "Add source stage", you can choose from many source providers, including CodeCommit, GitHub, S3, etc. Here we are going to cover two options, CodeCommit and GitHub.
- CodeCommit: Select CodeCommit as source provider. Follow steps here https://docs.aws.amazon.com/codecommit/latest/userguide/how-to-migrate-repository-existing.html to migrate your local repository to CodeCommit. Select the corresponding reposiroty name and branch name, leave detection options and artifact format as default.
<img width="1085" alt="Screenshot 2022-09-03 at 3 29 27 PM" src="https://user-images.githubusercontent.com/77185679/188285282-d2f16e13-100a-43d8-835a-9901bfcd2cf4.png">
<br/><br/>

- GitHub: Select GitHub (Version 2) as source provider. Click on Connect to GitHub. Follow steps here https://docs.aws.amazon.com/dtconsole/latest/userguide/connections-create-github.html to create a connection. Select the corresponding reposiroty name and branch name, leave everything else as default.
<img width="789" alt="Screenshot 2022-09-03 at 3 35 08 PM" src="https://user-images.githubusercontent.com/77185679/188285427-eb9e3703-c5ee-4c0c-b534-76d5c3bcaa20.png">
<br/><br/>

### Build Stage
At "Add build stage", select CodeBuild as build provider. Leave region as default and click on "Create project".

For Environment, use a managed image and select Ubuntu as OS. Select standard runtime, the latest image and Linux environment type. Allow it to create a new service role for this CodeBuild project.
<img width="792" alt="Screenshot 2022-09-03 at 3 42 18 PM" src="https://user-images.githubusercontent.com/77185679/188285592-c814f20f-db28-4a3f-bdf0-9da435508a96.png">
<br/><br/>

For Buildspec, leave everything as default. Later we are going to create a buildspec.yml file at the root directory of your project, which is a YAML file that provides instructions on the build process.
<img width="789" alt="Screenshot 2022-09-03 at 3 49 28 PM" src="https://user-images.githubusercontent.com/77185679/188285825-8809017d-0569-47ba-98b4-803d6214543c.png">
<br/><br/>

For Logs, you have the option to send build logs to CloudWatch/S3. You can create a group name for the log group to help you better identify it. <br/>
<img width="790" alt="Screenshot 2022-09-03 at 3 47 50 PM" src="https://user-images.githubusercontent.com/77185679/188285787-55b71bd5-bbd4-425a-8482-4464237e8336.png">
<br/><br/>

Click on "Continue to CodePipeline". Select the CodeBuild project created and click on "Next".
<img width="817" alt="Screenshot 2022-09-03 at 3 52 50 PM" src="https://user-images.githubusercontent.com/77185679/188285890-57e9073a-2758-42ee-98d3-9dda995185ba.png">
<br/><br/>

### Deploy Stage
At "Add deploy stage", since we are hosting our website on S3, select S3 as deploy provider. Choose the region where your website hosting bucket is located and select the bucket. Check "Extract file before deploy". By default, the build artifact generated by CodeBuild will be zipped, and this option will unzip it before deploying to the S3 bucket.
<img width="818" alt="Screenshot 2022-09-03 at 3 58 18 PM" src="https://user-images.githubusercontent.com/77185679/188286001-bfe49c97-850a-426c-a106-0eda15b37d35.png">
<br/><br/>

Click on "Next", review the stages and click on "Create pipeline".

### Add buildspec.yml File
After creating the pipeline, you will notice that it starts to execute and fails at the Build stage. If you click on "View in CodeBuild" under Build, you should see build logs suggesting that YAML file does not exist.
<img width="885" alt="Screenshot 2022-09-03 at 4 26 11 PM" src="https://user-images.githubusercontent.com/77185679/188286701-2bdc4596-c8be-484d-8910-c8240a6c82a4.png">
<br/><br/>

To fix this, copy the buildspec.yml file in this project to the root directory of your reposiroty, commit and push the change. The pipeline should be executing again and this time it should work.

### Test the CI/CD Pipeline
To test that the CI/CD pipeline is indeed working, try make some small changes in your code (e.g. changing background color of a page), commit and push the change. After CodePipeline finishes execution, you should see the change on your website by clicking website endpoint in S3.
