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
There are multiple ways you can host a static website on AWS, including S3, Amplify, EC2, etc. For this project, I chose to host it on S3 because it is the easiest to get started with and serverless.

CodeBuild, CodeDeploy were used to build CI/CD pipeline, and CodePipeline was used to orchestrate the process.

Route 53 was used to route a custom domain to the S3 bucket website endpoint.

[Optional] I set up a CloudFront distribution in front of the S3 bucket, so that the content can be cached in edge locations and access to S3 bucket can be restricted to CloudFront distribution with origin access control settings, which enhances security. To ensure that users always get the latest content from CloudFront, S3 Event Notifications were used to trigger a Lambda function whenever the bucket gets updated, to invalidate CloudFront cache.

## 1. Hosting React Website on S3
Let's forget about the CI/CD pipeline for now and just get our website working by manually upload it to S3.

First, create a new bucket in S3 for hosting the website. Uncheck "Block all public access" and leave everything else as default. This will allow people to access your website.
<img width="810" alt="Screenshot 2022-09-02 at 8 41 29 PM" src="https://user-images.githubusercontent.com/77185679/188249144-1d498418-f030-46a0-94f7-897794071b85.png">

In the bucket, go to Properties and scroll to the buttom to enable "Static website hosting". Set BOTH "Index document" and "Error document" to index.html. It's important to set "Error document" as well, otherwise the application won't be able to route to different paths (e.g. example.com/page1, example.com/page2).
<img width="786" alt="Screenshot 2022-09-02 at 8 47 54 PM" src="https://user-images.githubusercontent.com/77185679/188249291-14574024-9ed0-4728-bbb5-a2e0bbd04ea5.png">

In the bucket, under Permissions, edit bucket policy and click on "Policy generator".
Apply the following configurations. For Actions, select GetObject. 
<img width="994" alt="Screenshot 2022-09-02 at 9 17 38 PM" src="https://user-images.githubusercontent.com/77185679/188250305-a6c8a520-7b4f-4bd9-a277-ac08fd9089e3.png">
For ARN, go back to the edit bucket policy page, copy bucket ARN, and enter \<bucket ARN\>/* (e.g. arn:aws:s3:::react-website-hosting-project/*). It's important to add /\* after the bucket ARN, because this policy needs to be applied to all objects within the bucket, not the bucket itself.
<img width="1385" alt="Screenshot 2022-09-02 at 9 18 55 PM" src="https://user-images.githubusercontent.com/77185679/188250333-386fc22a-7664-4342-8f45-1534aa70bbdf.png">

Then click on Add Statement, Generate Policy, and copy the JSON policy to the edit policy page, save changes.
<img width="844" alt="Screenshot 2022-09-02 at 9 22 53 PM" src="https://user-images.githubusercontent.com/77185679/188250513-a27fb583-e627-4b82-9737-331fddfe3494.png">

Next, go to your React App. If you don't have a build already, run the following command to create a build:

npm install<br/>
npm run build

This should create a build folder under the root directory of your project. In the bucket, to go Objects, upload everything in the build folder to the S3 bucket. (Note: DO NOT upload the build folder as a folder, instead, upload individual files and upload any folder inside build folder as folder).

Now, you should be able to access your website by clicking the link under Properties -> Static website hosting -> Bucket website endpoint.
<img width="1286" alt="Screenshot 2022-09-02 at 9 49 48 PM" src="https://user-images.githubusercontent.com/77185679/188251279-e564545a-3376-420e-8552-7786f4aaa977.png">
