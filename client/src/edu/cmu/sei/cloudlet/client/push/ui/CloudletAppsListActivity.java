package edu.cmu.sei.cloudlet.client.push.ui;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import org.json.JSONException;
import org.json.JSONObject;

import edu.cmu.sei.cloudlet.client.CloudletReadyApp;
import edu.cmu.sei.cloudlet.client.CurrentCloudlet;
import edu.cmu.sei.cloudlet.client.R;
import edu.cmu.sei.cloudlet.client.TimeLog;
import edu.cmu.sei.cloudlet.client.models.ServiceVMInstance;
import edu.cmu.sei.cloudlet.client.net.CloudletCommandException;
import edu.cmu.sei.cloudlet.client.push.models.AppInfoObject;
import edu.cmu.sei.cloudlet.client.push.models.JSONToAppInfoObject;
import edu.cmu.sei.cloudlet.client.push.net.CloudletPushCommandSender;
import edu.cmu.sei.cloudlet.client.ui.ConnectionInfoFragment;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Environment;
import android.app.Activity;
import android.app.ProgressDialog;
import android.content.Context;
import android.content.Intent;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

public class CloudletAppsListActivity extends Activity 
{
    private static final String LOG_TAG = CloudletAppsListActivity.class.getName();
    
	private ListView listView;
	private List<AppInfoObject> appInfoObjects;
	private AppRowAdapter adapter;
	private HashMap<AppInfoObject, Boolean> showActions;
	private HashMap<AppInfoObject, Boolean> runningServers;
	
    private HashMap<AppInfoObject, ServiceVMInstance> runningServerIds;	

	private AppInfoObject appBeingInstalled;

	@Override
	protected void onCreate(Bundle savedInstanceState) 
	{
		super.onCreate(savedInstanceState);
		setContentView(R.layout.cloudlet_apps_list);
		
        showActions = new HashMap<AppInfoObject, Boolean>();
        runningServers = new HashMap<AppInfoObject, Boolean>();
        runningServerIds = new HashMap<AppInfoObject, ServiceVMInstance>();
        appInfoObjects = new ArrayList<AppInfoObject>();
        
		listView = (ListView)findViewById(R.id.listView);
		adapter = new AppRowAdapter(this, R.layout.cloudlet_app_item, appInfoObjects);
		listView.setAdapter(adapter);
		
        // Load cloudlet information.
        ConnectionInfoFragment connInfoFragment = (ConnectionInfoFragment) getFragmentManager().findFragmentById(R.id.connInfoPanel);
        connInfoFragment.setCloudletInfo(CurrentCloudlet.name, CurrentCloudlet.ipAddress);    		

		listView.setOnItemClickListener(new OnItemClickListener() {
			@Override
			public void onItemClick(AdapterView<?> arg0, View arg1, int arg2,
					long arg3) {
				AppInfoObject appInfo = appInfoObjects.get(arg2);

				if(showActions.get(appInfo)!=null && showActions.get(appInfo))
				{
					showActions.put(appInfo, false);
				}
				else
				{
					showActions.put(appInfo, true);
				}

				adapter.notifyDataSetChanged();
			}
		});

		new GetAppsListAsyncTask().execute();
	}

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		// Inflate the menu; this adds items to the action bar if it is present.
		getMenuInflater().inflate(R.menu.activity_main, menu);
		return true;
	}

	@Override
	public boolean onMenuItemSelected(int featureId, MenuItem item) {
		if(item.getItemId()==R.id.menu_installed_apps){
			startActivity( new Intent( CloudletAppsListActivity.this, InstalledApplcationListActivity.class ) );
			return true;
		}
        if(item.getItemId()==R.id.menu_refresh){
            new GetAppsListAsyncTask().execute();
            return true;
        }		
		return false;
	}
	
	protected boolean isInstalled(AppInfoObject appInfo)
	{
	    String appPackage = appInfo.getPackage();
	    Log.d("asd", appPackage);
	    
        List<ApplicationInfo> packages = getPackageManager().getInstalledApplications(PackageManager.GET_META_DATA);
        for (ApplicationInfo packageInfo : packages) 
        {
            boolean notSystemApp = (packageInfo.flags & ApplicationInfo.FLAG_SYSTEM) == 0;
            if(notSystemApp)
            {
                if(packageInfo.packageName.equals(appPackage))
                {
                    Log.d("", packageInfo.packageName + " is installed.");
                    return true;
                }
            }
        }
        
        return false;
	}

	/**
	 * @author GENE
	 * Class for async access to the application list
	 */
	class GetAppsListAsyncTask extends AsyncTask<Void, Integer, String>{
	    
	    private String lastErrorMessage = "";

		@Override
		protected String doInBackground(Void... params) {
			try {
			    TimeLog.reset();
			    TimeLog.stamp("Getting apps list.");
			    lastErrorMessage = "";
			    CloudletPushCommandSender sender = new CloudletPushCommandSender(CurrentCloudlet.ipAddress, CurrentCloudlet.port);                
                String response = sender.executeGetAppsList();
                sender.shutdown();
                TimeLog.stamp("App list received.");
                return response;
			}
            catch (CloudletCommandException e)
            {
                lastErrorMessage = e.getMessage();
                e.printStackTrace();
            }
			return null;
		}

		@Override
		protected void onPostExecute(String result) 
		{
			try 
			{
				if(result==null)
				{
					Toast.makeText(CloudletAppsListActivity.this, "Error getting app list: " + lastErrorMessage, Toast.LENGTH_SHORT).show();
					return;
				}
				appInfoObjects.clear();
				appInfoObjects.addAll(JSONToAppInfoObject.getAppInfoObjectsFromJSONString(result));
				adapter.notifyDataSetChanged();
			} catch (JSONException e) 
			{
				e.printStackTrace();
			}
		}
	}

	/**
	 * @author GENE
	 * Class for async access to the application list
	 */
	class DownloadAppAsyncTask extends AsyncTask<AppInfoObject, Integer, String>{
	    
	    private String lastErrorMessage = "";

		@Override
		protected String doInBackground(AppInfoObject... params) {
			try {
			    lastErrorMessage = "";
			    TimeLog.stamp("Sending app name to server.");
			    Log.d("", "Sending app name to server.");
			    appBeingInstalled = params[0]; 
				String appname = appBeingInstalled.getName();				
                File directory = new File(Environment.getExternalStorageDirectory() +"/downloaded_apks/");
                directory.mkdirs();
                String fileName = Environment.getExternalStorageDirectory() +"/downloaded_apks/"+appname + ".apk";				
				
                CloudletPushCommandSender sender = new CloudletPushCommandSender(CurrentCloudlet.ipAddress, CurrentCloudlet.port);
                sender.executeGetApp(appname, fileName);
                sender.shutdown();
                TimeLog.stamp("App received.");

				Intent intent = new Intent();
				intent.setAction(android.content.Intent.ACTION_VIEW);
				intent.setDataAndType(Uri.fromFile(new File(fileName)), "application/vnd.android.package-archive");
				
				TimeLog.stamp("Installing app.");
				startActivityForResult(intent, 5000); 
				
				return "ok";
			}
            catch (CloudletCommandException e)
            {
                lastErrorMessage = e.getMessage();
                e.printStackTrace();
            }
			return null;
		}
		
        @Override
        protected void onPostExecute(String result) 
        {
            if(result==null)
            {
                Toast.makeText(CloudletAppsListActivity.this, "Error getting app: " + lastErrorMessage, Toast.LENGTH_SHORT).show();
                return;
            }
        }		
	}
	
	@Override
	protected void onActivityResult(int requestCode, int resultCode, Intent data)
	{
	    TimeLog.stamp("App installed.");
	    try
        {
            TimeLog.writeToFile("pushlog.txt");
        }
        catch (IOException e)
        {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
	}

	class StartServerAsyncTask extends AsyncTask<AppInfoObject, Integer, String>{

        private String lastErrorMessage = "";	    
		ProgressDialog dialog;

		@Override
		protected void onPreExecute() {
			dialog = new ProgressDialog(CloudletAppsListActivity.this);
			dialog.setMessage("Starting server. Please wait");
			dialog.show();
		}

		@Override
		protected void onPostExecute(final String result) {
			dialog.dismiss();
			runOnUiThread(new Runnable() {
				@Override
				public void run() {
					if(result!=null){
						Log.e(CloudletAppsListActivity.class.getSimpleName(), result + "");
						adapter.notifyDataSetChanged();
					}
					else
					{
					    Toast.makeText(CloudletAppsListActivity.this, "Error starting server: " + lastErrorMessage, Toast.LENGTH_SHORT).show();
						Log.e(CloudletAppsListActivity.class.getSimpleName(), "result is null");
					}
				}
			});
		}

		@Override
		protected String doInBackground(AppInfoObject... params) {
			try 
			{
			    lastErrorMessage = "";
			    AppInfoObject currentAppInfo = params[0];
				String serviceId = params[0].getServiceId();
				Log.d(LOG_TAG, "Starting app for service id " + serviceId);
				
				CloudletPushCommandSender sender = new CloudletPushCommandSender(CurrentCloudlet.ipAddress, CurrentCloudlet.port);
                JSONObject jsonResponse = sender.executeStartVMRequest(serviceId, false);
                sender.shutdown();              
                
                ServiceVMInstance serverVMInstanceInfo = new ServiceVMInstance(jsonResponse);
                runningServerIds.put(currentAppInfo, serverVMInstanceInfo);

				runningServers.put(currentAppInfo, true);
				return "ok";
			}
            catch (CloudletCommandException e)
            {
                lastErrorMessage = e.getMessage();
                e.printStackTrace();
            }
			return null;
		}
	}
	
    class StopServerAsyncTask extends AsyncTask<AppInfoObject, Integer, String>{

        private String lastErrorMessage = "";
        ProgressDialog dialog;

        @Override
        protected void onPreExecute() {
            dialog = new ProgressDialog(CloudletAppsListActivity.this);
            dialog.setMessage("Stopping server. Please wait");
            dialog.show();
        }

        @Override
        protected void onPostExecute(final String result) {
            dialog.dismiss();
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    if(result!=null){
                        Log.e(CloudletAppsListActivity.class.getSimpleName(), result + "");
                        adapter.notifyDataSetChanged();
                    }
                    else
                    {
                        Toast.makeText(CloudletAppsListActivity.this, "Error stopping server: " + lastErrorMessage, Toast.LENGTH_SHORT).show();                        
                        Log.e(CloudletAppsListActivity.class.getSimpleName(), "result is null");
                    }
                }
            });
        }

        @Override
        protected String doInBackground(AppInfoObject... params) {
            try 
            {
                lastErrorMessage = "";
                AppInfoObject currentAppInfo = params[0];
                ServiceVMInstance serverVMInstanceInfo = runningServerIds.get(currentAppInfo);
                
                CloudletPushCommandSender sender = new CloudletPushCommandSender(CurrentCloudlet.ipAddress, CurrentCloudlet.port);
                sender.executeStopVMRequest(serverVMInstanceInfo.getInstanceId());
                sender.shutdown();              

                runningServers.put(currentAppInfo, false);
                runningServerIds.put(currentAppInfo, null);
                return "ok";
            }
            catch (CloudletCommandException e)
            {
                lastErrorMessage = e.getMessage();
                e.printStackTrace();
            }
            return null;
        }
    }	

	/**
	 * @author GENE
	 * Custom adapter view for the Application Info Objects
	 */
	class AppRowAdapter extends ArrayAdapter<AppInfoObject>{

		public AppRowAdapter(Context context, int textViewResourceId,
				List<AppInfoObject> objects) {
			super(context, textViewResourceId, objects);
		}

		@Override
		public View getView(int position, View convertView, ViewGroup parent) {

			View v = convertView;
			if( v == null )
			{
				LayoutInflater inflator = (LayoutInflater)getSystemService(LAYOUT_INFLATER_SERVICE);
				v = inflator.inflate(R.layout.cloudlet_app_item, null);
			}
			
			final AppInfoObject appInfoObject = appInfoObjects.get(position);
			TextView nameTextView = (TextView)v.findViewById(R.id.nameTextView);
			nameTextView.setText(appInfoObject.getName());
			
			TextView descriptionTextView = (TextView)v.findViewById(R.id.descriptionTextView);
			descriptionTextView.setText(appInfoObject.getDescription());
			
			TextView tagsTextView = (TextView)v.findViewById(R.id.tagsTextView);
			tagsTextView.setText(appInfoObject.getTags());
			
			TextView minRequiredViersionTextView = (TextView)v.findViewById(R.id.minRequiredVersionTextView);
			minRequiredViersionTextView.setText(appInfoObject.getMinRequiredVersion());
			
			TextView sha1hashTextView = (TextView)v.findViewById(R.id.sha1hashTextView);
			sha1hashTextView.setText(appInfoObject.getServiceId());
			
			TextView versionTextView = (TextView)v.findViewById(R.id.versionTextView);
			versionTextView.setText(appInfoObject.getVersion());
			
			LinearLayout actionsLayout = (LinearLayout)v.findViewById(R.id.actionsLayout);
			if(showActions.get(appInfoObject)!=null && showActions.get(appInfoObject))
				actionsLayout.setVisibility(View.VISIBLE);
			else
				actionsLayout.setVisibility(View.GONE);
			
			Button startServerButton = (Button)v.findViewById(R.id.start_server_button);
			
			if(runningServers.get(appInfoObject)!=null && runningServers.get(appInfoObject))
				startServerButton.setText("Stop Server");
			else
				startServerButton.setText("Start Server");
			
			startServerButton.setOnClickListener(new OnClickListener() 
			{
				@Override
				public void onClick(View v) 
				{
					if(runningServers.get(appInfoObject)!=null && runningServers.get(appInfoObject))
					{
					    new StopServerAsyncTask().execute(appInfoObject);				        
					}
					else
					{
						new StartServerAsyncTask().execute(appInfoObject);
					}
				}
			});
			
            Button downloadAppButton = (Button)v.findViewById(R.id.download_app_button);
            downloadAppButton.setText("Get App");  
            downloadAppButton.setOnClickListener(new OnClickListener() 
            {
                @Override
                public void onClick(View v) 
                {
                    new DownloadAppAsyncTask().execute(appInfoObject);
                }
            });             
			
			Button startAppButton = (Button)v.findViewById(R.id.start_app_button);
            startAppButton.setText("Start App");
			
            startAppButton.setOnClickListener(new OnClickListener() 
            {
                @Override
                public void onClick(View v) 
                {
                    if(isInstalled(appInfoObject))
                    {
                        // Start the cloudlet ready app.
                        String serviceId = appInfoObject.getServiceId();
                        ServiceVMInstance serverVMInstanceInfo = runningServerIds.get(appInfoObject);
                        if(serverVMInstanceInfo == null)
                        {
                            Toast.makeText(CloudletAppsListActivity.this, "Start a server before starting the app.", Toast.LENGTH_SHORT).show();
                        }
                        else
                        {
                            CloudletReadyApp app = new CloudletReadyApp(serviceId, serverVMInstanceInfo);
                            app.start(CloudletAppsListActivity.this);
                        }
                    }
                    else
                    {
                        Toast.makeText(CloudletAppsListActivity.this, "Application not yet installed.", Toast.LENGTH_SHORT).show();
                    }                    
                }
            });			
			
			return v;
		}
	}
}
