# -*- coding: utf-8 -*-

from tfsoffice import TwentyFour
import sys


def main(username, password, applicationid):
    # init api
    api = TwentyFour(username, password, applicationid)

    # save company
    # api.saveCompany('Tester igjen', companyType='Supplier', Id=433,
    #                 email_work='email_work@loyning.net',
    #                 email_invoice='email_invoice@loyning.net',
    #                 phone='123456789')

    # list companies
    # print 'CustomerId 433: ', api.listCompanies(CompanyId=433)
    # print '-- Categories --'
    # print api.listCompanyCategories(433)
    # print 'CustomerName *elias: ', api.listCompanies(CompanyName='elias')

    # save company categories
    # result = api.saveCompanyCategories(
    #     CompanyId=433, categories=['Blogger', ])
    # print 'saveCompanyCategories'
    # print result

    # get project client
    # client = api.getClient('Project')
    # status, project = client.service.GetSingleProject(317)
    # print project

    projects = api.findProject(CustomerId=108)
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
