#!/usr/bin/python

import unittest
import sys
from centos_package_cron import package_checker
from centos_package_cron import package_fetcher
from centos_package_cron import errata_fetcher
from centos_package_cron.errata_fetcher import ErrataType
from centos_package_cron.errata_fetcher import ErrataSeverity
from mock import Mock
from centos_package_cron.package import Package

class PackageCheckerTest(unittest.TestCase):
    def testAdvisoryPackageMeantForCurrentOsCentOs5(self):
        # arrange
        os_fetcher = Mock()
        os_fetcher.get_top_level_version = Mock(return_value='5')
        errata = Mock()
        pkg = Mock()
        checker = package_checker.PackageChecker(errata,pkg,os_fetcher)
        advisory_packages = [{'name': 'xen-libs','version':'3.0.3', 'release':'135.el4.2', 'arch':'x86_64'},
                             {'name': 'xen-libs','version':'3.0.3', 'release':'135.el5.2', 'arch':'x86_64'}]

        # act
        result = map(lambda a: checker._advisoryPackageMeantForCurrentOs(a), advisory_packages)

        # assert
        assert result == [False, True]

    def testAdvisoryPackageMeantForCurrentOsCentOs_AllVersions(self):
        # arrange
        os_fetcher = Mock()
        os_fetcher.get_top_level_version = Mock(return_value='6')
        errata = Mock()
        pkg = Mock()
        checker = package_checker.PackageChecker(errata,pkg,os_fetcher)
        advisory_packages = [{'name': 'xen-libs','version':'3.0.3',  'release':'135.el4.2', 'arch':'x86_64'},
                             {'name': 'kernel',  'version':'2.6.32', 'release':'642.13.1.el6', 'arch':'i686'},
                             {'name': 'xen-libs','version':'3.0.3',  'release':'135.el6.2', 'arch':'x86_64'}]

        # act
        result = map(lambda a: checker._advisoryPackageMeantForCurrentOs(a), advisory_packages)

        # assert
        assert result == [False, True, True]

    def testAdvisoryPackageMeantForCurrentOsCentOs7(self):
        # arrange
        os_fetcher = Mock()
        os_fetcher.get_top_level_version = Mock(return_value='7')
        errata = Mock()
        pkg = Mock()
        checker = package_checker.PackageChecker(errata,pkg,os_fetcher)
        advisory_packages = [{'name': 'xen-libs','version':'3.0.3', 'release':'135.el6.2', 'arch':'x86_64'},
                             {'name': 'xen-libs','version':'3.0.3', 'release':'135.el7.2', 'arch':'x86_64'},
                             {'name': 'xen-libs','version':'3.0.3', 'release':'135.el7_0.2', 'arch':'x86_64'}]

        # act
        result = map(lambda a: checker._advisoryPackageMeantForCurrentOs(a), advisory_packages)

        # assert
        assert result == [False, True, True]

    def testSameVersionOfAnotherPackageInstalled(self):
        # arrange
        errata = Mock()
        errata.get_errata = Mock(return_value=[
        errata_fetcher.ErrataItem('adv id', ErrataType.SecurityAdvisory,ErrataSeverity.Important, ['i686','x86_64'], ['7'], [{'name': 'libcacard-tools','version':'1.5.3', 'release':'60.el7_0.5', 'arch':'x86_64'}],[])
        ])
        pkg = Mock()
        pkg.fetch_installed_packages = Mock(return_value=[
                Package('libgcrypt', '1.5.3', '4.el7', 'x86_64', 'updates')
        ])
        os_fetcher = Mock()
        os_fetcher.get_top_level_version = Mock(return_value='7')
        os_fetcher.get_mid_level_version = Mock(return_value='7.0')
        checker = package_checker.PackageChecker(errata,pkg,os_fetcher)

        # act
        result = checker.findAdvisoriesOnInstalledPackages()

        # assert
        assert result == []

    def testFindAdvisoriesOnInstalledPackagesNotInstalled(self):
        # arrange
        errata = Mock()
        errata.get_errata = Mock(return_value=[
        errata_fetcher.ErrataItem('adv id', ErrataType.SecurityAdvisory,ErrataSeverity.Important, ['x86_64'], ['7'], [{'name': 'xen-libs','version':'3.0.3', 'release':'135.el5_8.2', 'arch':'x86_64'}],[])
        ])
        pkg = Mock()
        pkg.fetch_installed_packages = Mock(return_value=[
        Package('bash','1.0', '4.el7', 'x86_64', 'updates'),
        Package('openssl','2.0', '4.el7', 'x86_64', 'updates')
        ])
        os_fetcher = Mock()
        os_fetcher.get_top_level_version = Mock(return_value='7')
        os_fetcher.get_mid_level_version = Mock(return_value='7.0')
        checker = package_checker.PackageChecker(errata,pkg,os_fetcher)

        # act
        result = checker.findAdvisoriesOnInstalledPackages()

        # assert
        self.assertEquals(result, [])

    def testFindAdvisoriesOnInstalledPackagesInstalledButCurrentAlready(self):
        # arrange
        errata = Mock()
        errata.get_errata = Mock(return_value=[
        errata_fetcher.ErrataItem('adv id', ErrataType.SecurityAdvisory,ErrataSeverity.Important, ['x86_64'], ['7'], [{'name': 'xen-libs','version':'3.0.3', 'release':'135.el7.2', 'arch':'x86_64'}],[])
        ])
        pkg = Mock()
        pkg.fetch_installed_packages = Mock(return_value=[
        Package('xen-libs','3.0.3', '135.el7.2', 'x86_64', 'updates'),
        Package('openssl','2.0', '4.el7', 'x86_64', 'updates')
        ])
        os_fetcher = Mock()
        os_fetcher.get_top_level_version = Mock(return_value='7')
        os_fetcher.get_mid_level_version = Mock(return_value='7.0')
        checker = package_checker.PackageChecker(errata,pkg,os_fetcher)

        # act
        result = checker.findAdvisoriesOnInstalledPackages()

        # assert
        self.assertEquals(result, [])

    def testFindAdvisoriesOnInstalledPackagesInstalledButNewerVersion(self):
        # arrange
        errata = Mock()
        errata.get_errata = Mock(return_value=[
        errata_fetcher.ErrataItem('adv id', ErrataType.SecurityAdvisory,ErrataSeverity.Important, ['x86_64'], ['7'], [{'name': 'xen-libs','version':'3.0.3', 'release':'135.el7.2', 'arch':'x86_64'}],[])
        ])
        pkg = Mock()
        pkg.fetch_installed_packages = Mock(return_value=[
        Package('xen-libs','3.0.4', '135.el5_8.2', 'x86_64', 'updates'),
        Package('openssl','2.0', '4.el7', 'x86_64', 'updates')
        ])
        os_fetcher = Mock()
        os_fetcher.get_top_level_version = Mock(return_value='7')
        os_fetcher.get_mid_level_version = Mock(return_value='7.0')
        checker = package_checker.PackageChecker(errata,pkg,os_fetcher)

        # act
        result = checker.findAdvisoriesOnInstalledPackages()

        # assert
        self.assertEquals(result, [])

    def testFindAdvisoriesOnInstalledPackagesVersionComparisonWith2Digits(self):
        # arrange
        errata = Mock()
        errata_packages = [
         {'arch': 'x86_64',
          'name': 'glibc',
          'release': '55.el7.1',
          'version': '2.17'},
         {'arch': 'x86_64',
          'name': 'glibc',
          'release': '118.el7.3',
          'version': '2.5'}]
        errata.get_errata = Mock(return_value=[
        errata_fetcher.ErrataItem('adv id', ErrataType.SecurityAdvisory,ErrataSeverity.Important, ['x86_64'], ['7'], errata_packages,[])
        ])
        pkg = Mock()
        pkg.fetch_installed_packages = Mock(return_value=[
        Package('glibc','2.17', '55.el7.1', 'x86_64', 'updates'),
        ])
        os_fetcher = Mock()
        os_fetcher.get_top_level_version = Mock(return_value='7')
        os_fetcher.get_mid_level_version = Mock(return_value='7.0')
        checker = package_checker.PackageChecker(errata,pkg,os_fetcher)

        # act
        result = checker.findAdvisoriesOnInstalledPackages()

        # assert
        assert result == []

    def testFindAdvisoriesOnInstalledPackagesBothOldAndNewInstalled(self):
        # arrange
        errata = Mock()
        errata.get_errata = Mock(return_value=[
        errata_fetcher.ErrataItem('adv id', ErrataType.SecurityAdvisory,ErrataSeverity.Important, ['x86_64'], ['7'], [{'name': 'xen-libs','version':'3.0.3', 'release':'135.el7.2', 'arch':'x86_64'}],[])
        ])
        pkg = Mock()
        pkg.fetch_installed_packages = Mock(return_value=[
        Package('xen-libs','3.0.3', '132.el7.2', 'x86_64', 'updates'),
        Package('xen-libs','3.0.4', '135.el7.2', 'x86_64', 'updates'),
        Package('openssl','2.0', '4.el7', 'x86_64', 'updates')
        ])
        os_fetcher = Mock()
        os_fetcher.get_top_level_version = Mock(return_value='7')
        os_fetcher.get_mid_level_version = Mock(return_value='7.0')
        checker = package_checker.PackageChecker(errata,pkg,os_fetcher)

        # act
        result = checker.findAdvisoriesOnInstalledPackages()

        # assert
        assert result == []

    def testFindAdvisoriesOnInstalledPackagesInstalledButLowerVersion(self):
        # arrange
        errata = Mock()
        errata.get_errata = Mock(return_value=[
        errata_fetcher.ErrataItem('adv id', ErrataType.SecurityAdvisory,ErrataSeverity.Important, ['x86_64'], ['7'], [{'name': 'xen-libs','version':'3.0.3', 'release':'135.el7.2', 'arch':'x86_64'}],[])
        ])
        pkg = Mock()
        pkg.fetch_installed_packages = Mock(return_value=[
        Package('xen-libs','3.0.2', '135.el7.2', 'x86_64', 'updates'),
        Package('openssl','2.0', '4.el7', 'x86_64', 'updates')
        ])
        os_fetcher = Mock()
        os_fetcher.get_top_level_version = Mock(return_value='7')
        os_fetcher.get_mid_level_version = Mock(return_value='7.0')
        checker = package_checker.PackageChecker(errata,pkg,os_fetcher)

        # act
        result = checker.findAdvisoriesOnInstalledPackages()

        # assert
        self.assertNotEquals(result, [])

    def testFindAdvisoriesOnInstalledPackagesInstalledButNewerRelease(self):
        # arrange
        errata = Mock()
        errata.get_errata = Mock(return_value=[
        errata_fetcher.ErrataItem('adv id', ErrataType.SecurityAdvisory,ErrataSeverity.Important, ['x86_64'], ['7'], [{'name': 'xen-libs','version':'3.0.3', 'release':'135.el7.2', 'arch':'x86_64'}],[])
        ])
        pkg = Mock()
        pkg.fetch_installed_packages = Mock(return_value=[
        Package('xen-libs','3.0.3', '135.el7.3', 'x86_64', 'updates'),
        Package('openssl','2.0', '4.el7', 'x86_64', 'updates')
        ])
        os_fetcher = Mock()
        os_fetcher.get_top_level_version = Mock(return_value='7')
        os_fetcher.get_mid_level_version = Mock(return_value='7.0')
        checker = package_checker.PackageChecker(errata,pkg,os_fetcher)

        # act
        result = checker.findAdvisoriesOnInstalledPackages()

        # assert
        self.assertEquals(result, [])

    def testFindAdvisoriesOnInstalledPackagesInstalledAndNeedsUpdatingButWrongCentOsVersion(self):
        # arrange
        errata = Mock()
        errata.get_errata = Mock(return_value=[
        errata_fetcher.ErrataItem('adv id', ErrataType.SecurityAdvisory,ErrataSeverity.Important, ['x86_64'], ['7'], [{'name': 'xen-libs','version':'3.0.3', 'release':'135.el7.2', 'arch':'x86_64'}],[])
        ])
        pkg = Mock()
        pkg.fetch_installed_packages = Mock(return_value=[
        Package('xen-libs','3.0.3', '135.el7.1', 'x86_64', 'updates'),
        Package('openssl','2.0', '4.el6', 'x86_64', 'updates')
        ])
        os_fetcher = Mock()
        os_fetcher.get_top_level_version = Mock(return_value='6')
        os_fetcher.get_mid_level_version = Mock(return_value='6.0')
        checker = package_checker.PackageChecker(errata,pkg,os_fetcher)

        # act
        result = checker.findAdvisoriesOnInstalledPackages()

        # assert
        self.assertEquals(result, [])

    def testFindAdvisoriesOnInstalledPackagesInstalledAndNeedsUpdatingButWrongCentOsVersionOnPackage(self):
        # https://github.com/wied03/centos-package-cron/issues/5
        # arrange
        errata = Mock()
        adv_packages = [{'name': 'bash','version':'3.2', 'release':'33.el5.1', 'arch':'i386'},
                        {'name': 'bash','version':'3.2', 'release':'33.el5.1', 'arch':'src'},
                    {'name': 'bash','version':'3.2', 'release':'33.el5.1', 'arch':'x86_64'},
                    {'name': 'bash','version':'4.1.2', 'release':'15.el6_5.1', 'arch':'i686'},
                    {'name': 'bash','version':'4.1.2', 'release':'15.el6_5.1', 'arch':'src'},
                    {'name': 'bash','version':'4.1.2', 'release':'15.el6_5.1', 'arch':'x86_64'},
                    {'name': 'bash','version':'4.2.45', 'release':'5.el7_0.2', 'arch':'src'},
                    {'name': 'bash','version':'4.2.45', 'release':'5.el7_0.2', 'arch':'x86_64'}]
        errata.get_errata = Mock(return_value=[
        errata_fetcher.ErrataItem('adv id', ErrataType.SecurityAdvisory,ErrataSeverity.Important, ['x86_64'], ['5', '6', '7'], adv_packages,[])
        ])
        pkg = Mock()
        pkg.fetch_installed_packages = Mock(return_value=[
        Package('bash','4.1.2', '29.el6', 'x86_64', 'updates')
        ])
        os_fetcher = Mock()
        os_fetcher.get_top_level_version = Mock(return_value='6')
        os_fetcher.get_mid_level_version = Mock(return_value='6.6')
        checker = package_checker.PackageChecker(errata,pkg,os_fetcher)

        # act
        result = checker.findAdvisoriesOnInstalledPackages()

        # assert
        self.assertEquals(result, [])

    def testFindAdvisoriesOnInstalledPackagesInstalledAndNeedsUpdating(self):
        # arrange
        errata = Mock()
        advisory = errata_fetcher.ErrataItem('adv id', ErrataType.SecurityAdvisory,ErrataSeverity.Important, ['x86_64'], ['7'], [{'name': 'xen-libs','version':'3.0.3', 'release':'135.el7.2', 'arch':'x86_64'}],[])
        errata.get_errata = Mock(return_value=[advisory])
        pkg = Mock()
        xen_package = Package('xen-libs','3.0.3', '135.el7.1', 'x86_64', 'updates')
        pkg.fetch_installed_packages = Mock(return_value=[
        xen_package,
        Package('openssl','2.0', '4.el7', 'x86_64', 'updates')
        ])
        os_fetcher = Mock()
        os_fetcher.get_top_level_version = Mock(return_value='7')
        os_fetcher.get_mid_level_version = Mock(return_value='7.0')
        checker = package_checker.PackageChecker(errata,pkg,os_fetcher)

        # act
        result = checker.findAdvisoriesOnInstalledPackages()

        # assert
        assert len(result) == 1
        first = result[0]
        assert first['advisory'] == advisory
        assert first['installed_packages'] == [xen_package]


if __name__ == "__main__":
            unittest.main()
