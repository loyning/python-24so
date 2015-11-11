# -*- coding: utf-8 -*-

import sys
import os
PARENT_DIR = os.path.join(os.path.abspath(os.path.curdir), '')
sys.path.append(PARENT_DIR)
sys.path.append('..')
from tfsoffice import TwentyFour


def main(username, password, applicationid):
    # init api
    api = TwentyFour(username, password, applicationid)

    # save company
    # api.save_company('Tester igjen', companyType='Supplier', Id=433,
    #                 email_work='email_work@loyning.net',
    #                 email_invoice='email_invoice@loyning.net',
    #                 phone='123456789')

    # list companies
    print 'CustomerId 210: ', api.list_companies(CompanyId=210)
    print '-- Categories --'
    print api.list_company_categories(210)
    print 'CustomerName *elias: ', api.list_companies(CompanyName='maraton')

    # save company categories
    # result = api.save_companyCategories(
    #     CompanyId=433, categories=['Blogger', ])
    # print 'saveCompanyCategories'
    # print result

    # get project client
    # client = api.get_client('Project')
    # status, project = client.service.GetSingleProject(317)
    # print project

    projects = api.find_project(CustomerId=108)
    if projects:
        print 'Found %s projects' % len(projects)
        print projects
    else:
        print 'Found nothing'


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print 'Syntax: python %s [username] [password] ' \
            '[applicationid]' % sys.argv[0]
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]
    applicationid = sys.argv[3]
    main(username, password, applicationid)

    print 'Done!\n'
