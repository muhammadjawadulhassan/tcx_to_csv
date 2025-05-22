import streamlit as st
import xml.etree.ElementTree as ET
import io, csv

def parse_tcx_bytes(tcx_bytes):
    root = ET.fromstring(tcx_bytes)
    ns = {
        'tcx': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
        'ext': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2',
    }

    # in-memory buffers
    act_buf = io.StringIO()
    lap_buf = io.StringIO()
    track_buf = io.StringIO()

    act_writer   = csv.writer(act_buf,    delimiter=';')
    lap_writer   = csv.writer(lap_buf,    delimiter=';')
    track_writer = csv.writer(track_buf,  delimiter=';')

    # headers
    act_writer.writerow([
        "ActivityId","ActivitySport","CreatorName","ProductID"
    ])
    lap_writer.writerow([
        "ActivityId","LapNumber","TotalTimeSeconds","DistanceMeters","Calories",
        "AverageHeartRateBpm","MaximumHeartRateBpm","MaximumSpeed",
        "AvgRunCadence","MaxRunCadence","Intensity","StartTime","TriggerMethod"
    ])
    track_writer.writerow([
        "ActivityId","LapNumber","TrackNumber","AltitudeMeters","DistanceMeters",
        "RunCadence","Speed","HeartRateBpm","LatitudeDegrees","LongitudeDegrees","Time"
    ])

    # loop activities
    for activity in root.findall(".//tcx:Activity", ns):
        act_id      = activity.find("tcx:Id", ns).text
        sport       = activity.get("Sport", "Unknown")
        creator_el  = activity.find("tcx:Creator/tcx:Name", ns)
        product_el  = activity.find("tcx:Creator/tcx:ProductID", ns)
        creator = creator_el.text if creator_el is not None else ""
        product = product_el.text if product_el is not None else ""
        act_writer.writerow([act_id, sport, creator, product])

        # loop laps
        for lap_idx, lap in enumerate(activity.findall("tcx:Lap", ns), start=1):
            total_time_el = lap.find("tcx:TotalTimeSeconds", ns)
            distance_el   = lap.find("tcx:DistanceMeters",    ns)
            calories_el   = lap.find("tcx:Calories",          ns)
            avg_hr_el     = lap.find("tcx:AverageHeartRateBpm/tcx:Value", ns)
            max_hr_el     = lap.find("tcx:MaximumHeartRateBpm/tcx:Value", ns)
            max_speed_el  = lap.find("tcx:MaximumSpeed",      ns)
            avg_cad_el    = lap.find(".//tcx:Extensions/tcx:LX/tcx:AvgRunCadence", ns)
            max_cad_el    = lap.find(".//tcx:Extensions/tcx:LX/tcx:MaxRunCadence", ns)
            intensity_el  = lap.find("tcx:Intensity",         ns)
            start_time    = lap.get("StartTime", "")
            trigger_el    = lap.find("tcx:TriggerMethod",     ns)

            lap_writer.writerow([
                act_id,
                lap_idx,
                total_time_el.text if total_time_el is not None else "",
                distance_el.text   if distance_el   is not None else "",
                calories_el.text   if calories_el   is not None else "",
                avg_hr_el.text     if avg_hr_el     is not None else "",
                max_hr_el.text     if max_hr_el     is not None else "",
                max_speed_el.text  if max_speed_el  is not None else "",
                avg_cad_el.text    if avg_cad_el    is not None else "",
                max_cad_el.text    if max_cad_el    is not None else "",
                intensity_el.text  if intensity_el  is not None else "",
                start_time,
                trigger_el.text    if trigger_el    is not None else ""
            ])

            # loop trackpoints
            for tp_idx, tp in enumerate(lap.findall(".//tcx:Trackpoint", ns), start=1):
                time_el = tp.find("tcx:Time",                     ns)
                alt_el  = tp.find("tcx:AltitudeMeters",          ns)
                dist_el = tp.find("tcx:DistanceMeters",          ns)
                hr_el   = tp.find("tcx:HeartRateBpm/tcx:Value",   ns)

                # extension block for speed & cadence
                tpx = tp.find("tcx:Extensions/ext:TPX", ns)
                if tpx is not None:
                    speed_el       = tpx.find("ext:Speed",       ns)
                    run_cadence_el = tpx.find("ext:RunCadence",  ns)
                else:
                    speed_el = run_cadence_el = None

                # position
                pos = tp.find("tcx:Position", ns)
                if pos is not None:
                    lat_el = pos.find("tcx:LatitudeDegrees",  ns)
                    lon_el = pos.find("tcx:LongitudeDegrees", ns)
                else:
                    lat_el = lon_el = None

                track_writer.writerow([
                    act_id,
                    lap_idx,
                    tp_idx,
                    alt_el.text    if alt_el    is not None else "",
                    dist_el.text   if dist_el   is not None else "",
                    run_cadence_el.text if run_cadence_el is not None else "",
                    speed_el.text  if speed_el  is not None else "",
                    hr_el.text     if hr_el     is not None else "",
                    lat_el.text    if lat_el    is not None else "",
                    lon_el.text    if lon_el    is not None else "",
                    time_el.text   if time_el   is not None else ""
                ])

    return (
        act_buf.getvalue().encode('utf-8'),
        lap_buf.getvalue().encode('utf-8'),
        track_buf.getvalue().encode('utf-8')
    )

def main():
    st.title("TCX → CSV Converter (Still Updating)")
    uploaded = st.file_uploader("Upload your TCX file", type="tcx")
    if uploaded:
        st.info("Parsing…")
        activities_csv, laps_csv, tracks_csv = parse_tcx_bytes(uploaded.read())
        st.success("Done! Download your CSVs below:")
        st.download_button(
            "📥 Download activities.csv",
            data=activities_csv,
            file_name="activities.csv",
            mime="text/csv",
        )
        st.download_button(
            "📥 Download laps.csv",
            data=laps_csv,
            file_name="laps.csv",
            mime="text/csv",
        )
        st.download_button(
            "📥 Download tracks.csv (main file to use for readings)",
            data=tracks_csv,
            file_name="tracks.csv",
            mime="text/csv",
        )
# --- Footer ---
    st.markdown(
        """
        <style>
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            text-align: center;
            color: grey;
            font-size: 0.8em;
        }
        </style>
        <div class="footer">
            Made with tech in UniPG
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
