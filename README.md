# Deploy React App to AWS with CI/CD pipeline
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
There are multiple ways you can host a static website on AWS, including S3, Amplify, EC2, etc. For this project, **S3** was chosen because it is the easiest to get started with and serverless.

**CodeBuild**, **CodeDeploy** were used to build CI/CD pipeline, and **CodePipeline** was used to orchestrate the process.

A **CloudFront** distribution was set up in front of the S3 bucket, so that the content can be cached in edge locations to improve website performance, HTTPS connection can be established, and access to S3 bucket can be restricted to CloudFront distribution with origin access control settings, which enhances security. 

To ensure that users always get the latest content from CloudFront, **S3 Event Notifications** were used to trigger a **Lambda** function whenever the bucket gets updated to invalidate CloudFront cache. 

**Route 53** was used to route a custom domain to the CloudFront distribution domain name.
<br/><br/>


## 1. Host React Website on S3
Let's forget about the CI/CD pipeline for now and just get our website working by manually upload it to S3.

1. First, create a new bucket in S3 for hosting the website. Uncheck **Block all public access** and leave everything else as default. This will allow people to access your website.
<img width="810" alt="Screenshot 2022-09-02 at 8 41 29 PM" src="https://user-images.githubusercontent.com/77185679/188249144-1d498418-f030-46a0-94f7-897794071b85.png">
<br/><br/>

2. In the bucket, go to Properties and scroll to the buttom to enable **Static website hosting**. Set BOTH **Index document** and **Error document** to **index.html**. It's important to set **Error document** as well, otherwise the application won't be able to route to different paths (e.g. example.com/page1, example.com/page2).
<img width="786" alt="Screenshot 2022-09-02 at 8 47 54 PM" src="https://user-images.githubusercontent.com/77185679/188249291-14574024-9ed0-4728-bbb5-a2e0bbd04ea5.png">
<br/><br/>

3. In the bucket, under **Permissions**, edit bucket policy and click on **Policy generator**.
Apply the following configurations. For Actions, select **GetObject**. 
<img width="994" alt="Screenshot 2022-09-02 at 9 17 38 PM" src="https://user-images.githubusercontent.com/77185679/188250305-a6c8a520-7b4f-4bd9-a277-ac08fd9089e3.png">
<br/><br/>

4. For ARN, go back to the edit bucket policy page, copy bucket ARN, and enter \<bucket ARN\>/* (e.g. arn:aws:s3:::react-website-hosting-project/*). It's important to add /\* after the bucket ARN, because this policy needs to be applied to all objects within the bucket, not the bucket itself.
<img width="1385" alt="Screenshot 2022-09-02 at 9 18 55 PM" src="https://user-images.githubusercontent.com/77185679/188250333-386fc22a-7664-4342-8f45-1534aa70bbdf.png">
<br/><br/>

5. Then click on **Add Statement**, **Generate Policy**, and copy the JSON policy to the edit policy page, save changes.
<img width="844" alt="Screenshot 2022-09-02 at 9 22 53 PM" src="https://user-images.githubusercontent.com/77185679/188250513-a27fb583-e627-4b82-9737-331fddfe3494.png">
<br/><br/>

6. Next, go to your React App. If you don't have a build already, run the following command to create a build, which should create a build folder under the root directory of your project.
   ```
   npm install
   npm run build
   ```

7. In the bucket, to go Objects, upload everything in the build folder to the S3 bucket. (Note: DO NOT upload the build folder as a folder, instead, upload individual files and upload any folder inside build folder as folder).

8. Now, you should be able to access your website by clicking the link under **Properties** -> **Static website hosting** -> **Bucket website endpoint**.
<img width="1286" alt="Screenshot 2022-09-02 at 9 49 48 PM" src="https://user-images.githubusercontent.com/77185679/188251279-e564545a-3376-420e-8552-7786f4aaa977.png">
<br/><br/>


## 2. Set Up CI/CD Pipeline
CI/CD means continuous integration, continuous delivery and continuous deployment. In this project, **CodeBuild** is used for CI to generate build for the React App, **CodeDeploy** is used for CD to deploy the build generated to S3, and **CodePipeline** is used to orchestrate the whole process.

To get started, go to CodePipeline and click **Create pipeline**. Choose a pipeline name and allow it to create a new service role for the pipeline. This will give CodePipeline permissions to interact with other services.
<img width="1064" alt="Screenshot 2022-09-03 at 3 03 00 PM" src="https://user-images.githubusercontent.com/77185679/188284645-0ff26bad-5c71-4bc4-aa7b-deb65ac1443f.png">
<br/><br/>

### Source Stage
At **Add source stage**, you can choose from many source providers, including CodeCommit, GitHub, S3, etc. Here we are going to cover two options, **CodeCommit** and **GitHub**.
- CodeCommit: Select CodeCommit as source provider. Follow steps here https://docs.aws.amazon.com/codecommit/latest/userguide/how-to-migrate-repository-existing.html to migrate your local repository to CodeCommit. Select the corresponding reposiroty name and branch name, leave detection options and artifact format as default.
<img width="1085" alt="Screenshot 2022-09-03 at 3 29 27 PM" src="https://user-images.githubusercontent.com/77185679/188285282-d2f16e13-100a-43d8-835a-9901bfcd2cf4.png">
<br/><br/>

- GitHub: Select GitHub (Version 2) as source provider. Click on Connect to GitHub. Follow steps here https://docs.aws.amazon.com/dtconsole/latest/userguide/connections-create-github.html to create a connection. Select the corresponding reposiroty name and branch name, leave everything else as default.
<img width="789" alt="Screenshot 2022-09-03 at 3 35 08 PM" src="https://user-images.githubusercontent.com/77185679/188285427-eb9e3703-c5ee-4c0c-b534-76d5c3bcaa20.png">
<br/><br/>

### Build Stage
At **Add build stage**, select **CodeBuild** as build provider. Leave region as default and click on **Create project**.

For **Environment**, use a managed image and select Ubuntu as OS. Select standard runtime, the latest image and Linux environment type. Allow it to create a new service role for this CodeBuild project.
<img width="792" alt="Screenshot 2022-09-03 at 3 42 18 PM" src="https://user-images.githubusercontent.com/77185679/188285592-c814f20f-db28-4a3f-bdf0-9da435508a96.png">
<br/><br/>

For **Buildspec**, leave everything as default. Later we are going to create a buildspec.yml file at the root directory of your project, which is a YAML file that provides instructions on the build process.
<img width="789" alt="Screenshot 2022-09-03 at 3 49 28 PM" src="https://user-images.githubusercontent.com/77185679/188285825-8809017d-0569-47ba-98b4-803d6214543c.png">
<br/><br/>

For **Logs**, you have the option to send build logs to CloudWatch/S3. You can create a group name for the log group to help you better identify it. <br/>
<img width="790" alt="Screenshot 2022-09-03 at 3 47 50 PM" src="https://user-images.githubusercontent.com/77185679/188285787-55b71bd5-bbd4-425a-8482-4464237e8336.png">
<br/><br/>

Click on **Continue to CodePipeline**. Select the CodeBuild project created and click on **Next**.
<img width="817" alt="Screenshot 2022-09-03 at 3 52 50 PM" src="https://user-images.githubusercontent.com/77185679/188285890-57e9073a-2758-42ee-98d3-9dda995185ba.png">
<br/><br/>

### Deploy Stage
At **Add deploy stage**, since we are hosting our website on S3, select S3 as deploy provider. Choose the region where your website hosting bucket is located and select the bucket. Check **Extract file before deploy**. By default, the build artifact generated by CodeBuild will be zipped, and this option will unzip it before deploying to the S3 bucket.
<img width="818" alt="Screenshot 2022-09-03 at 3 58 18 PM" src="https://user-images.githubusercontent.com/77185679/188286001-bfe49c97-850a-426c-a106-0eda15b37d35.png">
<br/><br/>

Click on **Next**, review the stages and click on **Create pipeline**.

### Add buildspec.yml File
After creating the pipeline, you will notice that it starts to execute and fails at the Build stage. If you click on **View in CodeBuild** under Build, you should see build logs suggesting that YAML file does not exist.
<img width="885" alt="Screenshot 2022-09-03 at 4 26 11 PM" src="https://user-images.githubusercontent.com/77185679/188286701-2bdc4596-c8be-484d-8910-c8240a6c82a4.png">
<br/><br/>

To fix this, copy the **buildspec.yml** file in this project to the root directory of your reposiroty, commit and push the change. The file allows the build server to install npm, create build with **npm run build**, and output all files under build directory as artifacts to the next stage, which is CodeDeploy. <br/>
The pipeline should be executing again and this time it should work.
<img width="1078" alt="Screenshot 2022-09-03 at 5 27 01 PM" src="https://user-images.githubusercontent.com/77185679/188288162-6bc5dc80-49f2-4a67-8f1f-841426f46a0a.png">
<br/><br/>

### Test the CI/CD Pipeline
To test that the CI/CD pipeline is indeed working, try make some small changes in your code (e.g. changing background color of a page), commit and push the change. After CodePipeline finishes execution, you should see the change on your website by clicking website endpoint in S3.
<br/><br/>


## 3. Set up a CloudFront Distribution
Now we have a website hosted on S3 with CI/CD, but it has several problems:
- S3 website endpoint only supports HTTP, which is unsecure if the user is going to enter some sensitive information
- The S3 bucket lives only in one region, which makes accessing the website from other regions of the world slow
- Allowing direct access to S3 could be insecure, and there is no control over who can access the website

To solve the problems above, we can set up a CloudFront distribution in front of the S3 bucket.

### What is CloudFront
CloudFront is a Content Delivery Network (CDN) hosted by AWS, which caches content at more than 200 edge locations around the world to improve read performance. It supports HTTPS and several ways to control viewer access, which enhances security for your website. For more information, see https://aws.amazon.com/cloudfront/?nc=sn&loc=0

### Steps
1. Go to CloudFront, click on **Create distribution**.
2. Select your S3 bucket as origin domain.
3. For **Origin access**, select **Origin access control settings** and click on **Create control setting**. Leave everything as default and click on **Create**.
<img width="603" alt="Screenshot 2022-09-03 at 11 03 06 PM" src="https://user-images.githubusercontent.com/77185679/188295190-b7272f5e-4bcf-4938-a01e-7956f0fe8eb0.png">

4. In Settings, you can select which edge locations you want to use, which will affect the pricing.
<img width="458" alt="Screenshot 2022-09-03 at 11 06 24 PM" src="https://user-images.githubusercontent.com/77185679/188295285-1cdb65f0-fee8-4798-a55b-ff81bf7b8d8e.png">

5. For **Default root object**, enter **index.html**.
<img width="582" alt="Screenshot 2022-09-03 at 11 27 56 PM" src="https://user-images.githubusercontent.com/77185679/188295800-3d49455c-0ae3-43f0-9175-3e37edbaf957.png">

6. Click on **Create distribution**. You should see a notification at top of the page, asking you to update S3 bucket policy. Copy the policy.
<img width="1401" alt="Screenshot 2022-09-03 at 11 09 17 PM" src="https://user-images.githubusercontent.com/77185679/188295339-fd672e47-43ee-4972-805c-96e681b1b398.png">

7. Go to S3 bucket -> **Permissions**, edit bucket policy. Remove the existing policy and paste the copied policy. Click on **Save changes**.
<img width="690" alt="Screenshot 2022-09-03 at 11 12 26 PM" src="https://user-images.githubusercontent.com/77185679/188295425-a39ec722-cecd-4005-b7df-a80ebd2d1c9e.png">

> Previously, we were allowing anyone to perform GetObject on objects in our bucket. Now, only the CloudFront distribution can access bucket objects, which is much more secure.

8. Also under S3 Permissions, edit **Block public access**, check **Block all public access** and save changes. Because now we are accessing the bucket through CloudFront, the bucket no longer needs to be public. This follows the AWS least-priviledge principle. For more information, see https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html. Note that from this point, you will not be able to access your website through bucket website endpoint.
9. In the CloudFront distribution -> **Error pages**, create the following custom error response.
<img width="798" alt="Screenshot 2022-09-03 at 11 47 45 PM" src="https://user-images.githubusercontent.com/77185679/188296416-a21dcd0c-1c0c-422f-be96-3562d74d022b.png">

10. Wait several minutes for the change to be deployed, and then you should be able to access your website through the distribution domain name with HTTPS.
<img width="1100" alt="Screenshot 2022-09-03 at 11 48 38 PM" src="https://user-images.githubusercontent.com/77185679/188296435-f9991d9b-8792-459a-83aa-c7640f252040.png">
<br/><br/>

## 4. Create a Lambda Function to Invalidate CloudFront Cache
Now you have a CloudFront distribution in front of your S3 bucket to deliver content to your users. If you make some changes and push it to your repository, you will notice that CodePipeline gets triggered and S3 bucket is updated, but your website accessed through the CloudFront distribution is not updated. This is because by default, CloudFront cache has a TTL (time-to-live) of 24 hours, which means that CloudFront will not fetch new content from the S3 origin until 24 hours later.

To resolve this, setting a shorter TTL would create a lot of unnecessary requests to S3, which is very inefficient. A better solution is to only make a new request to S3 when the S3 bucket gets updated. A combination of S3 Event Notifications and a Lambda function is a perfect solution for this scenario.

### Introduction to AWS Lambda
AWS Lambda is a serverless compute service that runs your code in response to events and automatically manages the underlying compute resources for you. For mode information, see https://aws.amazon.com/lambda/. 

In this case, we can send S3 Event Notifications whenever the S3 bucket gets updated, which triggers a Lambda function that runs some code to invalidate the cache at the CloudFront distribution. After the cache being invalidated, accessing the CloudFront distribution will make it make a new request to the S3 bucket origin to get the latest content.

### Steps
1. Go to Lambda, click on **Create function**.
2. Select **Author from scratch**, enter a function name, select Python 3.9 as runtime. Leave other fields as default and **Create function**.
<img width="1295" alt="Screenshot 2022-09-04 at 3 00 21 PM" src="https://user-images.githubusercontent.com/77185679/188329334-4ff7b006-8c11-410f-aabe-4522bc56c671.png">

3. Copy the content of **invalidate_cloudfront_cache.py** in this repository and paste it to overwrite your Lambda function. Replace **DISTRIBUTION_ID** with the ID of your distribution. Click on **Deploy**.
<img width="633" alt="Screenshot 2022-09-04 at 3 04 52 PM" src="https://user-images.githubusercontent.com/77185679/188329513-d85a963c-2198-47a9-898a-b02608f31b18.png">

4. Now we need to give the Lambda function permissions to invalidate CloudFront cache. Go to **Configuration** -> **Permissions**, click on the execution role name, which will lead to an IAM page.
<img width="613" alt="Screenshot 2022-09-04 at 3 13 54 PM" src="https://user-images.githubusercontent.com/77185679/188329830-594425a1-1249-4b08-a99e-52169eadeef0.png">

5. Under Permissions, click on **Add permissions** -> **Create inline policy**.
<img width="1062" alt="Screenshot 2022-09-04 at 3 14 42 PM" src="https://user-images.githubusercontent.com/77185679/188329851-96cae942-1e3a-418e-b8bb-d6ffe66c13df.png">

6. Click on **JSON**, paste the following policy. Replace "Resource" value with your CloudFront distribution's ARN. Review and create the policy.

   ```
   {
      "Version": "2012-10-17",
      "Statement": [
          {
              "Effect": "Allow",
              "Action": "cloudfront:CreateInvalidation",
              "Resource": "arn:aws:cloudfront::621431699301:distribution/EA51AZF868RKT"
          }
      ]
   }
   ```

7. Go back to your Lambda function, clikc on **Code** -> **Test**. Create a new test event, leave everything as default and **Save**.
<img width="803" alt="Screenshot 2022-09-04 at 3 28 12 PM" src="https://user-images.githubusercontent.com/77185679/188330381-82cb24a8-569d-4928-81cf-4c14ef3dc49d.png">

8. Click on **Test** again to run the test. You should see the following response. This means that the cache at the CloudFront distribution has been invalidated.
<img width="1048" alt="Screenshot 2022-09-04 at 3 29 36 PM" src="https://user-images.githubusercontent.com/77185679/188330423-6f18436c-1f94-4dfa-b15c-59414b9039cf.png">

9. Go to your website through the CloudFront distribution domain name, and you should be able to see changes you made previously.
10. Now let's configure S3 Event Notifications to let it triggers the Lambda function automatically to invalidate CloudFront cache in case of a S3 bucket update. Go to your bucket, under **Properties** -> **Event notifications**, click on **Create event notification**.
<img width="1282" alt="Screenshot 2022-09-04 at 3 35 03 PM" src="https://user-images.githubusercontent.com/77185679/188330588-65835943-7d00-452d-b5d4-1415e44d2bf8.png">

11. Create a name for the event, leave prefix and suffix empty. For **Event types**, select all events under **Object creation**, **Object removal** and **Object restore**.
<img width="775" alt="Screenshot 2022-09-04 at 3 37 17 PM" src="https://user-images.githubusercontent.com/77185679/188330665-b0ee120a-b341-4ac6-99ff-4a83b084d245.png">

12. For **Destination**, select your Lambda function. **Save changes**.
<img width="796" alt="Screenshot 2022-09-04 at 3 38 01 PM" src="https://user-images.githubusercontent.com/77185679/188330683-fd3de64e-22b5-4a83-ae36-f5e243eedd48.png">

13. Push some other changes to your repository. After CodePipeline finishes execution, you should be able to see your website gets updated thourgh CloudFront access.


