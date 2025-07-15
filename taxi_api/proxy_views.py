"""
Proxy views to download NYC taxi data from host machine
since Docker containers are blocked from accessing CloudFront
"""

import requests
import tempfile
import os
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.conf import settings
import subprocess


class TaxiDataProxyView(View):
    """Proxy view to download taxi data from host machine"""
    
    def get(self, request, year, month):
        """Download and serve parquet data"""
        url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year}-{month:02d}.parquet"
        
        try:
            # Use curl from host machine if available
            tmp_path = f"/tmp/taxi_data_{year}_{month:02d}.parquet"
            
            # Try to download using curl from host
            curl_cmd = f"curl -L -o {tmp_path} '{url}'"
            result = subprocess.run(curl_cmd, shell=True, 
                                  capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(tmp_path):
                # Serve the file
                with open(tmp_path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/octet-stream')
                    response['Content-Disposition'] = f'attachment; filename="yellow_tripdata_{year}-{month:02d}.parquet"'
                    return response
            else:
                return JsonResponse({'error': f'Failed to download: {result.stderr}'}, status=500)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
