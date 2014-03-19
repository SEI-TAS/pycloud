package edu.cmu.sei.cloudlet.client.synth.ui;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

import android.app.AlertDialog;
import android.app.ListActivity;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.os.Bundle;
import android.os.Environment;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.BaseAdapter;
import android.widget.TextView;
import edu.cmu.sei.cloudlet.client.synth.models.OverlayInfo;

/**
 * This list activity shows a list of all the overlays on the SD card.
 * 
 * @author ssimanta
 * 
 */
public class OverlayList extends ListActivity implements OnItemClickListener
{
    public static final String LOG_TAG = OverlayList.class.getName();
    
    // Directory on the SD Card that stores the overlays folders.
    public static final String CLOUDLET_OVERLAY_DIR = Environment.getExternalStorageDirectory() + "/cloudlet/overlays";    

    public static final int MENU_OPTION_REFRESH = 1;
    
    protected ArrayList<String> overlayFileNamesList;
    protected BaseAdapter overlayFileNamesListAdapter;

    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);

        setTitle("Cloudlet Overlays");

        loadOverlayList();

        getListView().setOnItemClickListener(this);
    }

    private void loadOverlayList()
    {
        final File overlayDirectory = new File(CLOUDLET_OVERLAY_DIR);

        // make sure the overlay directory exists on the SD card
        boolean dirExists = checkOverlayDirExistence(overlayDirectory);

        if (dirExists)
        {
            overlayFileNamesList = new ArrayList<String>(
                    getOverlayFileNames(overlayDirectory));

        }
        else
        {
            overlayFileNamesList = new ArrayList<String>();
            overlayFileNamesList.add("Overlay directory ["
                    + CLOUDLET_OVERLAY_DIR
                    + "] doesn't exist on the SD card");
        }

        overlayFileNamesListAdapter = new OverlayNameListAdapter(this,
                overlayFileNamesList);
        setListAdapter(overlayFileNamesListAdapter);
    }

    protected boolean checkOverlayDirExistence(final File overlayDir)
    {
        if (overlayDir != null && overlayDir.exists())
        {
            Log.i(LOG_TAG, "Overlay directory " + overlayDir.getAbsolutePath()
                    + " exists.");
            return true;
        }
        else
        {
            // Create the required folders if missing.
            Log.i(LOG_TAG, "The cloudlet overlay file directory doesn't exist "
                    + CLOUDLET_OVERLAY_DIR
                    + " exists; creating it.");
            overlayDir.mkdirs();

            // If we weren't able to create the folder, just notify the user.
            if (!overlayDir.exists())
            {
                AlertDialog.Builder builder = new AlertDialog.Builder(this);
                builder.setTitle("Overlay Directory Does not Exist");
                final TextView message = new TextView(this);
                message.setText("The directory " + overlayDir.getAbsolutePath()
                        + " doesn't exist and could not be created.");
                builder.setView(message);
                builder.setPositiveButton("Done",
                        new DialogInterface.OnClickListener()
                        {
                            @Override
                            public void onClick(DialogInterface dialog,
                                    int which)
                            {
                            }
                        });

                builder.create().show();
                return false;
            }
            else
            {
                return true;
            }
        }
    }

    protected List<String> getOverlayFileNames(File overlayDir)
    {
        List<String> list = new ArrayList<String>();

        // Get all the subdirectories of the overlay dir.
        File[] subfolderList = overlayDir.listFiles();
        if (subfolderList == null || subfolderList.length == 0)
        {
            list.add("Overlay directory ["
                    + CLOUDLET_OVERLAY_DIR
                    + "] doesn't contain any overlay folders.");
            return list;
        }
        else
        {
            for (File folder : subfolderList)
            {
                if(folder.isDirectory())
                {
                    // Check if it actually contains an overlay.
                    try
                    {
                        OverlayInfo overlayInfo = new OverlayInfo(folder.getAbsolutePath());
                        list.add(folder.getName());
                    }
                    catch(RuntimeException e)
                    {
                        Log.w(LOG_TAG, "Ignoring folder with no valid overlay: " + folder.getName());
                    }                    
                }
            }
        }

        return list;
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu)
    {
        super.onPrepareOptionsMenu(menu);
        menu.add(0, MENU_OPTION_REFRESH, 0, "Refresh");
        return true;
    }

    @Override
    public boolean onMenuItemSelected(int featureId, MenuItem item)
    {
        switch (item.getItemId())
        {
            case MENU_OPTION_REFRESH:
                loadOverlayList();
                break;
        }
        return true;

    }

    @Override
    public void onItemClick(final AdapterView<?> arg0, View arg1,
            final int itemclicked, long arg3)
    {

        String clickedFileName = (String) this.overlayFileNamesListAdapter
                .getItem(itemclicked);

        if (clickedFileName != null)
        {
            
            Intent intent = new Intent(this, VMSynthesisActivity.class);
            intent.putExtra(VMSynthesisActivity.INTENT_EXTRA_BASE_OVERLAY_FOLDER,
                    CLOUDLET_OVERLAY_DIR);
            intent.putExtra(VMSynthesisActivity.INTENT_EXTRA_USER_SELECTED_OVERLAY_FOLDER,
                            clickedFileName);
            startActivity(intent);
        }
    }

}

class OverlayNameListAdapter extends BaseAdapter
{

    private List<String> fileNames;
    private Context context;

    public OverlayNameListAdapter(final Context ctx,
            final List<String> infileNames)
    {
        fileNames = infileNames;
        context = ctx;

    }

    @Override
    public int getCount()
    {
        return fileNames.size();
    }

    @Override
    public Object getItem(int position)
    {
        return fileNames.get(position);
    }

    @Override
    public long getItemId(int position)
    {
        return position;
    }

    @Override
    public void notifyDataSetChanged()
    {
        super.notifyDataSetChanged();
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent)
    {

        View v = convertView;
        TextView tv;

        if (v == null)
            tv = new TextView(context);
        else
            tv = ((TextView) convertView);

        tv.setText(fileNames.get(position));
        tv.setPadding(15, 10, 15, 10);
        tv.setTextSize(15);

        return tv;

    }

}
