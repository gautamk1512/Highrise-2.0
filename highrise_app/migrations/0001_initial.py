# Generated by Django 5.0.3 on 2024-07-16 06:07

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CorporatesList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('corpo_name', models.TextField(blank=True, max_length=255, null=True)),
                ('status', models.TextField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='CorporateType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('corpo_type', models.TextField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EventAcc',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Event_name', models.TextField(blank=True, max_length=500, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('type', models.CharField(blank=True, max_length=100, null=True)),
                ('num_lead', models.IntegerField(blank=True, null=True)),
                ('event_details', models.TextField(blank=True, max_length=5000, null=True)),
                ('name', models.TextField(blank=True, max_length=255, null=True)),
                ('num_attendees', models.TextField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EventType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.TextField(blank=True, max_length=255, null=True)),
                ('status', models.TextField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='HomeVisit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, max_length=255, null=True)),
                ('C_name', models.TextField(blank=True, max_length=255, null=True)),
                ('C_ph', models.TextField(blank=True, max_length=255, null=True)),
                ('date', models.DateField(blank=True, null=True)),
                ('detail', models.TextField(blank=True, max_length=255, null=True)),
                ('Site_name', models.TextField(blank=True, max_length=255, null=True)),
                ('images', models.ImageField(blank=True, null=True, upload_to='HomeVisit/')),
                ('co_fellow', models.CharField(blank=True, max_length=5000, null=True)),
                ('visit_type', models.CharField(blank=True, max_length=250, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Members',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uname', models.CharField(blank=True, max_length=100, null=True)),
                ('member_name', models.CharField(blank=True, max_length=200, null=True)),
                ('mobile', models.IntegerField(blank=True, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('designation', models.CharField(blank=True, max_length=100)),
                ('pwd', models.TextField(blank=True, max_length=100, null=True)),
                ('status', models.IntegerField(default=1)),
                ('role', models.IntegerField(db_comment='2 is team leader role', default=0)),
            ],
        ),
        migrations.CreateModel(
            name='SageMitraList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sm_name', models.TextField(blank=True, max_length=255, null=True)),
                ('sm_ph', models.TextField(blank=True, max_length=255, null=True)),
                ('status', models.TextField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='SiteVisit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, max_length=255, null=True)),
                ('C_name', models.TextField(blank=True, max_length=255, null=True)),
                ('C_ph', models.TextField(blank=True, max_length=255, null=True)),
                ('date', models.DateField(blank=True, null=True)),
                ('detail', models.TextField(blank=True, max_length=255, null=True)),
                ('Site_name', models.TextField(blank=True, max_length=255, null=True)),
                ('visit_stage', models.TextField(blank=True, max_length=255, null=True)),
                ('images', models.ImageField(blank=True, null=True, upload_to='HomeVisit/')),
                ('co_fellow', models.CharField(blank=True, max_length=5000, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Target',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, max_length=255, null=True)),
                ('status', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CorpFormData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visit_date', models.DateField(default=datetime.date.today)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('corp_name', models.CharField(blank=True, max_length=500, null=True)),
                ('meet_person', models.IntegerField(blank=True, null=True)),
                ('presentation', models.CharField(blank=True, choices=[('done', 'done'), ('not_done', 'not_done')], max_length=500, null=True)),
                ('cofel_name', models.CharField(blank=True, max_length=500, null=True)),
                ('nxt_pre_date', models.DateField(blank=True, null=True)),
                ('reason', models.TextField(blank=True, max_length=500, null=True)),
                ('key_person', models.CharField(max_length=255, null=True)),
                ('images', models.ImageField(blank=True, null=True, upload_to='CorpoVisit/')),
                ('key_person_contact', models.TextField(blank=True, max_length=255, null=True)),
                ('data_collect', models.TextField(blank=True, max_length=500, null=True)),
                ('key_person2', models.TextField(blank=True, max_length=255, null=True)),
                ('key_person_contact2', models.TextField(blank=True, max_length=255, null=True)),
                ('corp_type', models.TextField(blank=True, max_length=255, null=True)),
                ('visit_type', models.TextField(blank=True, max_length=255, null=True)),
                ('location', models.TextField(blank=True, max_length=255, null=True)),
            ],
            options={
                'indexes': [models.Index(fields=['name'], name='highrise_ap_name_cf5c20_idx'), models.Index(fields=['visit_date'], name='highrise_ap_visit_d_c7692d_idx')],
            },
        ),
        migrations.CreateModel(
            name='FollowUpData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ROW_NUM', models.TextField(blank=True, max_length=500, null=True)),
                ('Name', models.TextField(blank=True, max_length=500, null=True)),
                ('Enquiry_SrNo', models.IntegerField(blank=True, null=True)),
                ('Edate', models.DateTimeField(blank=True, null=True)),
                ('GTC', models.TextField(blank=True, max_length=500, null=True)),
                ('SourceEnquiry', models.TextField(blank=True, max_length=500, null=True)),
                ('Source', models.TextField(blank=True, max_length=500, null=True)),
                ('Employee_Name', models.TextField(blank=True, max_length=500, null=True)),
                ('EnquiryStage', models.TextField(blank=True, max_length=500, null=True)),
                ('FollowUp_Id', models.IntegerField(blank=True, null=True)),
                ('Remark1', models.TextField(blank=True, max_length=500, null=True)),
                ('Remark2', models.TextField(blank=True, max_length=500, null=True)),
                ('Remark3', models.TextField(blank=True, max_length=500, null=True)),
                ('Next_FollowUp1', models.DateTimeField(blank=True, null=True)),
                ('Status_Desc', models.TextField(blank=True, max_length=500, null=True)),
                ('Mobile', models.TextField(blank=True, max_length=500, null=True)),
                ('Phone_Office', models.TextField(blank=True, max_length=500, null=True)),
                ('Phone_Resi', models.TextField(blank=True, max_length=500, null=True)),
                ('Mobile2', models.TextField(blank=True, max_length=500, null=True)),
                ('Phone_Resi2', models.TextField(blank=True, max_length=500, null=True)),
                ('Phone_Offi2', models.TextField(blank=True, max_length=500, null=True)),
                ('SOEnquiry_Id2', models.TextField(blank=True, max_length=500, null=True)),
                ('FollowUpEmployee_Id', models.TextField(blank=True, max_length=500, null=True)),
                ('EnquiryStage_Id', models.TextField(blank=True, max_length=500, null=True)),
                ('SOEnquiry_Id', models.TextField(blank=True, max_length=500, null=True)),
                ('Enquiry_id', models.TextField(blank=True, max_length=500, null=True)),
                ('FollowUp_Date', models.DateTimeField(blank=True, null=True)),
                ('Reffered_project1', models.TextField(blank=True, max_length=500, null=True)),
                ('Reffered_project2', models.TextField(blank=True, max_length=500, null=True)),
                ('CustomerGrade', models.TextField(blank=True, max_length=500, null=True)),
                ('Priority', models.TextField(blank=True, max_length=500, null=True)),
                ('Broker_Name', models.TextField(blank=True, max_length=500, null=True)),
                ('Broker_PH', models.TextField(blank=True, max_length=500, null=True)),
                ('Prospect_Location', models.TextField(blank=True, max_length=500, null=True)),
                ('city', models.TextField(blank=True, max_length=500, null=True)),
                ('Occupation', models.TextField(blank=True, max_length=500, null=True)),
                ('SourceFunding', models.TextField(blank=True, max_length=500, null=True)),
                ('Employee_id', models.TextField(blank=True, max_length=500, null=True)),
                ('Projnm1', models.TextField(blank=True, max_length=500, null=True)),
                ('Projnm2', models.TextField(blank=True, max_length=500, null=True)),
                ('Email', models.TextField(blank=True, max_length=500, null=True)),
                ('Email2', models.TextField(blank=True, max_length=500, null=True)),
                ('Remark', models.TextField(blank=True, max_length=500, null=True)),
                ('Final_Remark', models.TextField(blank=True, max_length=500, null=True)),
                ('UNITTYPENM', models.TextField(blank=True, max_length=500, null=True)),
                ('Budget', models.TextField(blank=True, max_length=500, null=True)),
                ('CustomerType', models.TextField(blank=True, max_length=500, null=True)),
                ('Result', models.TextField(blank=True, max_length=500, null=True)),
                ('Next_Followup_Employee', models.TextField(blank=True, max_length=500, null=True)),
                ('FollowUp_Mode', models.TextField(blank=True, max_length=500, null=True)),
                ('FollowUp_ModeF_Age', models.TextField(blank=True, max_length=500, null=True)),
                ('F_Due_Age', models.TextField(blank=True, max_length=500, null=True)),
                ('Resource_URL', models.TextField(blank=True, max_length=500, null=True)),
                ('OverdueDays', models.TextField(blank=True, max_length=500, null=True)),
                ('FollowUp_Count', models.TextField(blank=True, max_length=500, null=True)),
                ('Account_ID', models.TextField(blank=True, max_length=500, null=True)),
            ],
            options={
                'indexes': [models.Index(fields=['Employee_Name'], name='highrise_ap_Employe_8b811e_idx'), models.Index(fields=['Next_FollowUp1'], name='highrise_ap_Next_Fo_348f14_idx'), models.Index(fields=['FollowUp_Date'], name='highrise_ap_FollowU_bcb596_idx')],
            },
        ),
        migrations.CreateModel(
            name='HighRiseData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ROW_NUM', models.TextField(blank=True, null=True)),
                ('Column1', models.TextField(blank=True, null=True)),
                ('Enquiry_id', models.TextField(blank=True, null=True)),
                ('Enquiry_SrNo', models.TextField(blank=True, null=True)),
                ('EDate', models.DateTimeField(blank=True, null=True)),
                ('Name', models.TextField(blank=True, max_length=1000, null=True)),
                ('Project', models.TextField(blank=True, max_length=1000, null=True)),
                ('Unit', models.TextField(blank=True, max_length=1000, null=True)),
                ('Mobile', models.TextField(blank=True, null=True)),
                ('Phone_Office', models.TextField(blank=True, max_length=1000, null=True)),
                ('Email', models.TextField(blank=True, max_length=1000, null=True)),
                ('Mobile2', models.TextField(blank=True, max_length=1000, null=True)),
                ('Phone_Offi2', models.IntegerField(blank=True, null=True)),
                ('Email2', models.TextField(blank=True, null=True)),
                ('Remark', models.TextField(blank=True, max_length=1000, null=True)),
                ('Result', models.TextField(blank=True, max_length=1000, null=True)),
                ('Final_Remark', models.TextField(blank=True, max_length=1000, null=True)),
                ('Remark1', models.TextField(blank=True, max_length=1000, null=True)),
                ('Remark2', models.TextField(blank=True, max_length=1000, null=True)),
                ('Remark3', models.TextField(blank=True, max_length=1000, null=True)),
                ('HandledByEmployee', models.TextField(blank=True, max_length=1000, null=True)),
                ('FollowUp_Date', models.DateTimeField(blank=True, null=True)),
                ('Followup_Employee', models.TextField(blank=True, max_length=1000, null=True)),
                ('Approach_Followup_Employee', models.TextField(blank=True, max_length=1000, null=True)),
                ('FollowUp_Mode', models.TextField(blank=True, max_length=1000, null=True)),
                ('Next_FollowUp1', models.DateTimeField(blank=True, null=True)),
                ('Next_Followup_Employee', models.TextField(blank=True, max_length=1000, null=True)),
                ('SourceEnquiry', models.TextField(blank=True, max_length=1000, null=True)),
                ('CustomerGrade', models.TextField(blank=True, max_length=1000, null=True)),
                ('Address', models.TextField(blank=True, max_length=1000, null=True)),
                ('Address_Temp', models.TextField(blank=True, max_length=1000, null=True)),
                ('Prospect_Location', models.TextField(blank=True, max_length=1000, null=True)),
                ('City', models.TextField(blank=True, max_length=1000, null=True)),
                ('Pin', models.TextField(blank=True, max_length=1000, null=True)),
                ('NRI', models.TextField(blank=True, max_length=1000, null=True)),
                ('Age', models.IntegerField(blank=True, null=True)),
                ('Phone_Resi', models.TextField(blank=True, max_length=1000, null=True)),
                ('Phone_Resi2', models.TextField(blank=True, max_length=1000, null=True)),
                ('Website', models.TextField(blank=True, max_length=1000, null=True)),
                ('Community', models.TextField(blank=True, max_length=1000, null=True)),
                ('Nation', models.TextField(blank=True, max_length=1000, null=True)),
                ('Family_Members', models.TextField(blank=True, default=None, null=True)),
                ('Staying_Status', models.TextField(blank=True, max_length=1000, null=True)),
                ('Marital_Status', models.TextField(blank=True, max_length=1000, null=True)),
                ('Occupation', models.TextField(blank=True, max_length=1000, null=True)),
                ('Income', models.TextField(blank=True, max_length=1000, null=True)),
                ('Organization', models.TextField(blank=True, max_length=1000, null=True)),
                ('Designation', models.TextField(blank=True, max_length=1000, null=True)),
                ('Office_Address', models.TextField(blank=True, max_length=1000, null=True)),
                ('Fax', models.TextField(blank=True, max_length=1000, null=True)),
                ('Contact_Person', models.TextField(blank=True, max_length=1000, null=True)),
                ('UNITTYPENM', models.TextField(blank=True, max_length=1000, null=True)),
                ('Rooms', models.TextField(blank=True, max_length=1000, null=True)),
                ('Toilets_Required', models.TextField(blank=True, max_length=1000, null=True)),
                ('Area_Requirement', models.TextField(blank=True, max_length=1000, null=True)),
                ('Parking', models.TextField(blank=True, max_length=1000, null=True)),
                ('Location', models.TextField(blank=True, max_length=1000, null=True)),
                ('Location2', models.TextField(blank=True, max_length=1000, null=True)),
                ('Location3', models.TextField(blank=True, max_length=1000, null=True)),
                ('Floor', models.TextField(blank=True, max_length=1000, null=True)),
                ('Budget', models.TextField(blank=True, max_length=1000, null=True)),
                ('SourceFunding', models.TextField(blank=True, max_length=1000, null=True)),
                ('Loan_required', models.TextField(blank=True, max_length=1000, null=True)),
                ('Loan_amount', models.TextField(blank=True, max_length=1000, null=True)),
                ('Finance', models.TextField(blank=True, max_length=1000, null=True)),
                ('Expected_Possation', models.TextField(blank=True, max_length=1000, null=True)),
                ('Enquirytype', models.TextField(blank=True, max_length=1000, null=True)),
                ('Broker_Name', models.TextField(blank=True, max_length=1000, null=True)),
                ('Source', models.TextField(blank=True, max_length=1000, null=True)),
                ('Campaign', models.TextField(blank=True, max_length=1000, null=True)),
                ('Primary_Source', models.TextField(blank=True, max_length=1000, null=True)),
                ('Secondary_Source', models.TextField(blank=True, max_length=1000, null=True)),
                ('Source_Of_Information', models.TextField(blank=True, max_length=1000, null=True)),
                ('FirstQuestion', models.TextField(blank=True, max_length=1000, null=True)),
                ('Action_taken', models.TextField(blank=True, max_length=1000, null=True)),
                ('Purchase_Before', models.TextField(blank=True, max_length=1000, null=True)),
                ('Booked_upto', models.TextField(blank=True, max_length=1000, null=True)),
                ('Projnm2', models.TextField(blank=True, max_length=1000, null=True)),
                ('Unitno2', models.TextField(blank=True, max_length=1000, null=True)),
                ('Bldg', models.TextField(blank=True, max_length=1000, null=True)),
                ('SalesPoints', models.TextField(blank=True, max_length=1000, null=True)),
                ('CustomerType', models.TextField(blank=True, max_length=1000, null=True)),
                ('EnquiryStage', models.TextField(blank=True, max_length=1000, null=True)),
                ('Enquiry_Status', models.TextField(blank=True, max_length=1000, null=True)),
                ('Enquiry_Conclusion_Date', models.DateTimeField(blank=True, null=True)),
                ('StageChangeDate', models.DateTimeField(blank=True, null=True)),
                ('Last_Approach_Date', models.TextField(blank=True, max_length=1000, null=True)),
                ('Filtered_Date', models.TextField(blank=True, max_length=1000, null=True)),
                ('Booking_Info', models.TextField(blank=True, max_length=1000, null=True)),
                ('Account_ID', models.TextField(max_length=1000, null=True)),
            ],
            options={
                'indexes': [models.Index(fields=['HandledByEmployee'], name='highrise_ap_Handled_7ac311_idx'), models.Index(fields=['EDate'], name='highrise_ap_EDate_3407a1_idx'), models.Index(fields=['Next_FollowUp1'], name='highrise_ap_Next_Fo_fd3d8b_idx'), models.Index(fields=['FollowUp_Date'], name='highrise_ap_FollowU_218b09_idx'), models.Index(fields=['StageChangeDate'], name='highrise_ap_StageCh_a322bb_idx'), models.Index(fields=['EnquiryStage'], name='highrise_ap_Enquiry_1ec8cd_idx'), models.Index(fields=['Enquirytype'], name='highrise_ap_Enquiry_284d45_idx')],
            },
        ),
        migrations.CreateModel(
            name='IpData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, null=True)),
                ('patient_name', models.TextField(blank=True, max_length=255, null=True)),
                ('key_person', models.TextField(blank=True, max_length=255, null=True)),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Ip', to='highrise_app.members')),
            ],
        ),
        migrations.CreateModel(
            name='AdmissionData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, null=True)),
                ('f_name', models.TextField(blank=True, max_length=255, null=True)),
                ('s_name', models.TextField(blank=True, max_length=255, null=True)),
                ('vertical', models.TextField(blank=True, max_length=255, null=True)),
                ('branch_class', models.TextField(blank=True, max_length=255, null=True)),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Admission', to='highrise_app.members')),
            ],
        ),
        migrations.CreateModel(
            name='Sagemitra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uname', models.CharField(blank=True, max_length=255, null=True)),
                ('SM_name', models.CharField(blank=True, max_length=255, null=True)),
                ('followUp_date', models.DateField(blank=True, null=True)),
                ('No_leads', models.IntegerField(blank=True, null=True)),
                ('lead_detail', models.TextField(blank=True, max_length=255, null=True)),
                ('sm_contact', models.TextField(blank=True, max_length=255, null=True)),
                ('new_sm_name', models.TextField(blank=True, max_length=255, null=True)),
                ('new_sm_contact', models.TextField(blank=True, max_length=255, null=True)),
                ('submission_date', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'indexes': [models.Index(fields=['uname'], name='highrise_ap_uname_53aa69_idx'), models.Index(fields=['followUp_date'], name='highrise_ap_followU_f54257_idx')],
            },
        ),
        migrations.CreateModel(
            name='EmpSetTarget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target', models.IntegerField(blank=True, null=True)),
                ('month', models.TextField(blank=True, null=True)),
                ('year', models.TextField(blank=True, null=True)),
                ('date', models.DateField(auto_now=True)),
                ('target_value', models.IntegerField(blank=True, null=True)),
                ('stage', models.IntegerField(blank=True, null=True)),
                ('Employee', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='Member_table', to='highrise_app.members')),
                ('Target', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='Target_table', to='highrise_app.target')),
            ],
        ),
        migrations.CreateModel(
            name='Target_Assign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target', models.IntegerField(blank=True, null=True)),
                ('revised_target', models.IntegerField(blank=True, null=True)),
                ('month', models.TextField(blank=True, null=True)),
                ('year', models.TextField(blank=True, null=True)),
                ('target_rev_date', models.DateField(blank=True, null=True)),
                ('date', models.DateField(auto_now=True)),
                ('Employee', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='highrise_app.members')),
                ('Target', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='highrise_app.target')),
            ],
        ),
        migrations.CreateModel(
            name='Teams',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('T_name', models.CharField(default=None, max_length=100)),
                ('status', models.CharField(choices=[('0', '0'), ('1', '1')], db_comment='0 = active and 1 = not active', default='0', max_length=1)),
                ('team_head_id', models.IntegerField(blank=True, null=True)),
                ('date', models.DateField(default=None)),
            ],
            options={
                'indexes': [models.Index(fields=['T_name'], name='highrise_ap_T_name_efc5c6_idx')],
            },
        ),
        migrations.AddField(
            model_name='members',
            name='team',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='highrise_app.teams'),
        ),
        migrations.AddIndex(
            model_name='members',
            index=models.Index(fields=['uname'], name='highrise_ap_uname_3f5ced_idx'),
        ),
        migrations.AddIndex(
            model_name='members',
            index=models.Index(fields=['member_name'], name='highrise_ap_member__686cfb_idx'),
        ),
    ]
