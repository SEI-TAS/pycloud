package edu.cmu.sei.cloudlet.client.caching.ui;

import android.app.Activity;
import android.app.ProgressDialog;
import android.content.Context;
import android.os.AsyncTask;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.*;
import edu.cmu.sei.ams.cloudlet.Service;
import edu.cmu.sei.ams.cloudlet.ServiceVM;
import edu.cmu.sei.cloudlet.client.CloudletReadyApp;
import edu.cmu.sei.cloudlet.client.CurrentCloudlet;
import edu.cmu.sei.cloudlet.client.R;
import edu.cmu.sei.cloudlet.client.ui.ConnectionInfoFragment;
import org.slf4j.ext.XLogger;
import org.slf4j.ext.XLoggerFactory;

import java.util.ArrayList;
import java.util.List;

/**
 * User: jdroot
 * Date: 3/21/14
 * Time: 10:38 AM
 */
public class ListServicesActivity extends Activity
{
    private static XLogger log = XLoggerFactory.getXLogger(ListServicesActivity.class);

    private ServiceRowAdapter adapter;
    private List<Service> serviceObjects;

    private ProgressDialog mProgressDialog = null;

    @Override
    protected void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.cloudlet_services_list);

        ConnectionInfoFragment connInfoFragment = (ConnectionInfoFragment) getFragmentManager().findFragmentById(R.id.connInfoPanel);
        connInfoFragment.setCloudletInfo(CurrentCloudlet.name, CurrentCloudlet.ipAddress);

        ListView listView = (ListView)findViewById(R.id.listView);
        serviceObjects = new ArrayList<Service>();
        adapter = new ServiceRowAdapter(this, R.layout.cloudlet_app_item, serviceObjects);
        listView.setAdapter(adapter);
//        listView.setOnItemClickListener(new AdapterView.OnItemClickListener()
//        {
//            @Override
//            public void onItemClick(AdapterView<?> adapterView, View view, int i, long l)
//            {
//                log.info("Starting service");
//                new StartServiceAsync().execute(serviceObjects.get(i));
//            }
//        });

        new GetServicesListAsync().execute();
    }


    private class ServiceRowAdapter extends ArrayAdapter<Service>
    {
        public ServiceRowAdapter(Context context, int textViewResourceId, List<Service> objects)
        {
            super(context, textViewResourceId, objects);
        }

        public View getView(int position, View convertView, final ViewGroup parent)
        {
            View v = convertView;
            if( v == null )
            {
                LayoutInflater inflator = (LayoutInflater)getSystemService(LAYOUT_INFLATER_SERVICE);
                v = inflator.inflate(R.layout.cloudlet_service_item, null);
            }

            final Service service = getItem(position);

            TextView idTextView = (TextView)v.findViewById(R.id.idTextView);
            TextView descriptionTextView = (TextView)v.findViewById(R.id.descriptionTextView);

            idTextView.setText(service.getServiceId());
            descriptionTextView.setText(service.getServiceId());

            final Button startStopServiceBtn = (Button)v.findViewById(R.id.startStopServiceButton);
            final Button startAppBtn = (Button)v.findViewById(R.id.startAppButton);

            final boolean running = service.getServiceVM() != null;

            if (running)
                startStopServiceBtn.setText("Stop Service");
            else
                startStopServiceBtn.setText("Start Service");

            startStopServiceBtn.setOnClickListener(new View.OnClickListener()
            {
                @Override
                public void onClick(View view)
                {
                    new StartStopServiceAsync(service, startStopServiceBtn, startAppBtn).execute();
                }
            });

            startAppBtn.setOnClickListener(new View.OnClickListener()
            {
                @Override
                public void onClick(View view)
                {
                    if (service.getServiceVM() != null)
                    {
                        CloudletReadyApp app = new CloudletReadyApp(service);
                        app.start(ListServicesActivity.this);
                    }
                    else
                        Toast.makeText(ListServicesActivity.this, "Unable to start app, there is no running server", Toast.LENGTH_SHORT).show();
                }
            });

            return v;
        }
    }


    private class StartStopServiceAsync extends AsyncTask<Void, Void, Boolean>
    {
        private Service service;
        private Button startStopButton;
        private Button appButton;

        private StartStopServiceAsync(Service service, Button startStopButton, Button appButton)
        {
            this.service = service;
            this.startStopButton = startStopButton;
            this.appButton = appButton;
        }

        @Override
        protected void onPreExecute()
        {
            mProgressDialog = new ProgressDialog(ListServicesActivity.this);
            mProgressDialog.setTitle("Service VM");
            mProgressDialog.setIndeterminate(false);
            mProgressDialog.setProgressStyle(ProgressDialog.STYLE_SPINNER);
            if (service.getServiceVM() == null)
                mProgressDialog.setMessage("Starting Service VM");
            else
                mProgressDialog.setMessage("Stopping Service VM");
            mProgressDialog.show();
        }

        @Override
        protected Boolean doInBackground(Void... voids)
        {
            if (service.getServiceVM() == null)
            {
                service.startService();
                return true;
            }
            else
            {
                service.stopService();
                return false;
            }
        }

        @Override
        protected void onPostExecute(Boolean startedOrStopped)
        {
            if (mProgressDialog != null)
                mProgressDialog.dismiss();
            if (startedOrStopped.booleanValue())
            {
                if (service.getServiceVM() == null) //Failed to start
                {
                    Toast.makeText(ListServicesActivity.this, "Error while starting service!", Toast.LENGTH_SHORT).show();
                    startStopButton.setText("Start Service");
                    appButton.setEnabled(false);
                }
                else
                {
                    Toast.makeText(ListServicesActivity.this, "Service started!", Toast.LENGTH_SHORT).show();
                    startStopButton.setText("Stop Service");
                    appButton.setEnabled(true);
                }
            }
            else
            {
                if (service.getServiceVM() == null) //Stopped
                {
                    Toast.makeText(ListServicesActivity.this, "Service stopped!", Toast.LENGTH_SHORT).show();
                    startStopButton.setText("Start Service");
                    appButton.setEnabled(false);
                }
                else
                {
                    Toast.makeText(ListServicesActivity.this, "Error while stopping service!", Toast.LENGTH_SHORT).show();
                    startStopButton.setText("Stop Service");
                    appButton.setEnabled(true);
                }
            }
        }
    }

    private class GetServicesListAsync extends AsyncTask<Void, Void, List<Service>>
    {

        private Exception e;

        @Override
        protected void onPreExecute()
        {
            mProgressDialog = new ProgressDialog(ListServicesActivity.this);
            mProgressDialog.setTitle("Querying Services");
            mProgressDialog.setIndeterminate(false);
            mProgressDialog.setProgressStyle(ProgressDialog.STYLE_SPINNER);
            mProgressDialog.setMessage("Getting services from " + CurrentCloudlet.cloudlet.getName());
            mProgressDialog.show();
        }

        @Override
        protected List<Service> doInBackground(Void... voids)
        {
            try
            {
                log.info("Running in background!");
                return CurrentCloudlet.cloudlet.getServices();
            }
            catch (Exception e)
            {
                log.info("Running in background!");
                this.e = e;
                return null;
            }
        }

        @Override
        protected void onPostExecute(List<Service> services)
        {
            if (mProgressDialog != null)
                mProgressDialog.dismiss();


            if (services == null)
            {
                Toast.makeText(ListServicesActivity.this, "Error getting app list: " + e.getMessage(), Toast.LENGTH_SHORT).show();
                return;
            }
            log.info("Got " + services.size() + " services");
            serviceObjects.clear();
            serviceObjects.addAll(services);
            adapter.notifyDataSetChanged();
        }
    }
}
