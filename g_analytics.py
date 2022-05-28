from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange
from google.analytics.data_v1beta.types import Dimension
from google.analytics.data_v1beta.types import Metric
from google.analytics.data_v1beta.types import RunReportRequest
from flask import current_app
from datetime import date, timedelta
from logging import getLogger

logger = getLogger('gunicorn.error')


class GAnalyzer:

    @classmethod
    def get_visitors_per_day(cls):
        property_id = current_app.config['GOOGLE_ANALYTICS_PROPERTY_ID']
        start_normal_date = date.today() - timedelta(days = 2)
        start_date = start_normal_date.isoformat()

        client = BetaAnalyticsDataClient()

        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="city")],
            metrics=[Metric(name="activeUsers")],
            date_ranges=[DateRange(start_date=start_date, end_date="today")],
        )
        response = client.run_report(request)
        country_visitors = []
        for row in response.rows:
            country_visitors.append((row.dimension_values[0].value, row.metric_values[0].value))

        return country_visitors

    @classmethod
    def get_visitors_per_month(cls):
        property_id = current_app.config['GOOGLE_ANALYTICS_PROPERTY_ID']
        start_normal_date = date.today() - timedelta(days = 30)
        start_date = start_normal_date.isoformat()

        client = BetaAnalyticsDataClient()

        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="city")],
            metrics=[Metric(name="activeUsers")],
            date_ranges=[DateRange(start_date=start_date, end_date="today")],
        )
        response = client.run_report(request)
        country_visitors = []
        for row in response.rows:
            country_visitors.append((row.dimension_values[0].value, row.metric_values[0].value))

        return country_visitors

    @classmethod
    def get_visitors_per_year(cls):
        property_id = current_app.config['GOOGLE_ANALYTICS_PROPERTY_ID']
        start_normal_date = date.today() - timedelta(days = 365)
        start_date = start_normal_date.isoformat()

        client = BetaAnalyticsDataClient()

        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="city")],
            metrics=[Metric(name="activeUsers")],
            date_ranges=[DateRange(start_date=start_date, end_date="today")],
        )
        response = client.run_report(request)
        country_visitors = []
        for row in response.rows:
            country_visitors.append((row.dimension_values[0].value, row.metric_values[0].value))

        return country_visitors

    @classmethod
    def get_visitors_chart_week(cls):
        property_id = current_app.config['GOOGLE_ANALYTICS_PROPERTY_ID']
        start_normal_date = date.today() - timedelta(days = 7)
        start_date = start_normal_date.isoformat()

        client = BetaAnalyticsDataClient()

        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="dayOfWeek")],
            metrics=[Metric(name="activeUsers")],
            date_ranges=[DateRange(start_date=start_date, end_date="today")],
        )
        response = client.run_report(request)
        weekly_visitors = {'name': 'Visitors','data': []}
        days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
        for row in response.rows:
            weekly_visitors['data'].append({
                'x': days[int(row.dimension_values[0].value)],
                'y': row.metric_values[0].value})

        logger.info(weekly_visitors)
        return [weekly_visitors]

    @classmethod
    def get_visitors_chart_month(cls):
        property_id = current_app.config['GOOGLE_ANALYTICS_PROPERTY_ID']
        start_normal_date = date.today() - timedelta(days = 365)
        start_date = start_normal_date.isoformat()

        client = BetaAnalyticsDataClient()

        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="month")],
            metrics=[Metric(name="activeUsers")],
            date_ranges=[DateRange(start_date=start_date, end_date="today")],
        )
        response = client.run_report(request)
        monthly_visitors = {'name': 'Visitors','type':'bar','data': []}
        months = {'01':'Jan','02': 'Feb', '03': 'Mar', '04': 'April', '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'}
        for row in response.rows:
            monthly_visitors['data'].append({
                'x': months[row.dimension_values[0].value],
                'y': row.metric_values[0].value})

        logger.info(monthly_visitors)
        return [monthly_visitors]

    @classmethod
    def get_visitors_chart_year(cls):
      
        property_id = current_app.config['GOOGLE_ANALYTICS_PROPERTY_ID']
        start_normal_date = date.today() - timedelta(days = 3650)
        start_date = start_normal_date.isoformat()

        client = BetaAnalyticsDataClient()

        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="year")],
            metrics=[Metric(name="activeUsers")],
            date_ranges=[DateRange(start_date=start_date, end_date="today")],
        )
        response = client.run_report(request)
        yearly_visitors = {'name': 'Visitors','type':'bar','data': []}
        
        for row in response.rows:
            yearly_visitors['data'].append({
                'x': row.dimension_values[0].value,
                'y': row.metric_values[0].value})

        return [yearly_visitors]


