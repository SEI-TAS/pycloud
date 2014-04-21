package edu.cmu.sei.cloudlet.client.ui;

import android.app.Activity;
import android.app.ProgressDialog;
import android.content.Context;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Environment;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.*;
import edu.cmu.sei.ams.cloudlet.*;
import edu.cmu.sei.ams.cloudlet.rank.CpuBasedRanker;
import edu.cmu.sei.cloudlet.client.CloudletReadyApp;
import edu.cmu.sei.cloudlet.client.CurrentCloudlet;
import edu.cmu.sei.cloudlet.client.R;
import edu.cmu.sei.cloudlet.client.synth.models.OverlayInfo;

import java.io.File;
import java.util.ArrayList;
import java.util.List;


/**
 * User: jdroot
 * Date: 4/18/14
 * Time: 9:49 AM
 */
public class CloudletSelectionActivity extends Activity
{
    private static final String CLOUDLET_OVERLAY_DIR = Environment.getExternalStorageDirectory() + "/cloudlet/overlays";
    private OverlayListAdapter adapter;
    private List<String> serviceObjects;
    private ProgressDialog mProgressDialog = null;

    @Override
    protected void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.cloudlet_services_list_no_header);

        ListView lv = (ListView) findViewById(R.id.listView);
        serviceObjects = new ArrayList<String>();

        adapter = new OverlayListAdapter(this, R.layout.cloudlet_service_item_no_header, serviceObjects);
        lv.setAdapter(adapter);

        lv.setOnItemClickListener(new AdapterView.OnItemClickListener()
        {
            @Override
            public void onItemClick(AdapterView<?> adapterView, View view, int i, long l)
            {
                String item = (String) adapterView.getItemAtPosition(i);
                Log.v("CLOUDLET", "SERVICE VM ID: " + item);
                new FindCloudletAsync(item).execute();
            }
        });

        new GetServicesListAsync().execute();
    }



    private enum State
    {
        LOOKING_FOR_CLOUDLET,
        GETTING_SERVICE,
        STARTING_SERVICE
    }

    private class FindCloudletAsync extends AsyncTask<Void, Void, Cloudlet>
    {
        private String service;

        private FindCloudletAsync(String service)
        {
            this.service = service;
        }

        @Override
        protected void onPreExecute()
        {
            mProgressDialog = new ProgressDialog(CloudletSelectionActivity.this);
            mProgressDialog.setTitle("Cloudlet");
            mProgressDialog.setIndeterminate(false);
            mProgressDialog.setProgressStyle(ProgressDialog.STYLE_SPINNER);
            mProgressDialog.setMessage("Looking for Cloudlet");
            mProgressDialog.show();
        }

        @Override
        protected Cloudlet doInBackground(Void... voids)
        {
            return CloudletFinder.findCloudletForService(service, new CpuBasedRanker());
        }

        @Override
        protected void onPostExecute(Cloudlet result)
        {
            if (mProgressDialog != null)
                mProgressDialog.dismiss();


            if (result == null)
                Toast.makeText(CloudletSelectionActivity.this, "Failed to find a nearby Cloudlet for the selected service", Toast.LENGTH_LONG).show();
            else
                new StartServiceAsync(service, result).execute();
        }
    }


    private class StartServiceAsync extends AsyncTask<Void, Void, ServiceVM>
    {
        private String service;
        private Cloudlet cloudlet;

        private StartServiceAsync(String service, Cloudlet cloudlet)
        {
            this.service = service;
            this.cloudlet = cloudlet;
        }

        @Override
        protected void onPreExecute()
        {
            mProgressDialog = new ProgressDialog(CloudletSelectionActivity.this);
            mProgressDialog.setTitle("Cloudlet: " + cloudlet.getName());
            mProgressDialog.setIndeterminate(false);
            mProgressDialog.setProgressStyle(ProgressDialog.STYLE_SPINNER);
            mProgressDialog.setMessage("Starting service");
            mProgressDialog.show();
        }


        @Override
        protected ServiceVM doInBackground(Void... voids)
        {
            try
            {
                Service s = cloudlet.getServiceById(service);
                if (s == null)
                    return null;
                return s.startService();
            }
            catch (CloudletException e)
            {
                return null;
            }
        }

        @Override
        protected void onPostExecute(ServiceVM result)
        {
            if (mProgressDialog != null)
                mProgressDialog.dismiss();

            if (result == null)
                Toast.makeText(CloudletSelectionActivity.this, "Failed to start the service", Toast.LENGTH_LONG).show();
            else //Service was started
            {
                CloudletReadyApp app = new CloudletReadyApp(result);
                app.start(CloudletSelectionActivity.this);
            }
        }
    }

    private class OverlayListAdapter extends ArrayAdapter<String>
    {
        private int resourceId;
        public OverlayListAdapter(Context context, int textViewResourceId, List<String> objects)
        {
            super(context, textViewResourceId, objects);
            this.resourceId = textViewResourceId;
        }

        @Override
        public View getView(int position, View convertView, ViewGroup parent)
        {
            View v = convertView;
            if( v == null )
            {
                LayoutInflater inflator = (LayoutInflater)getSystemService(LAYOUT_INFLATER_SERVICE);
                v = inflator.inflate(resourceId, null);
            }

            final String service = getItem(position);

            TextView idTextView = (TextView)v.findViewById(R.id.idTextView);

            idTextView.setText(service);

            return v;
        }
    }

    private class GetServicesListAsync extends AsyncTask<Void, Void, List<String>>
    {

        private Exception e;

        @Override
        protected void onPreExecute()
        {
            mProgressDialog = new ProgressDialog(CloudletSelectionActivity.this);
            mProgressDialog.setTitle("Services");
            mProgressDialog.setIndeterminate(false);
            mProgressDialog.setProgressStyle(ProgressDialog.STYLE_SPINNER);
            mProgressDialog.setMessage("Looking for nearby services");
            mProgressDialog.show();
        }

        @Override
        protected List<String> doInBackground(Void... voids)
        {
            return CloudletFinder.findAllNearbyServices();
        }

        @Override
        protected void onPostExecute(List<String> services)
        {
            if (mProgressDialog != null)
                mProgressDialog.dismiss();

            serviceObjects.clear();
            serviceObjects.addAll(services);
            adapter.notifyDataSetChanged();
        }
    }
}
