import streamlit as st
import xml.etree.ElementTree as ET
import io, csv

# --- 1) Parse TCX bytes into three CSV byte-streams ---
def parse_tcx_bytes(tcx_bytes):
    root = ET.fromstring(tcx_bytes)
    ns = {
        'tcx': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
        'ext': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2'
    }

    # prepare in-memory buffers
    act_buf = io.StringIO()
    lap_buf = io.StringIO()
    track_buf = io.StringIO()

    act_writer = csv.writer(act_buf, delimiter=';')
    lap_writer = csv.writer(lap_buf, delimiter=';')
    track_writer = csv.writer(track_buf, delimiter=';')

    # write headers
    act_writer.writerow(["ActivityId","ActivitySport","CreatorName","ProductID"])
    lap_writer.writerow([
        "ActivityId","LapNumber","TotalTimeSeconds","DistanceMeters","Calories",
        "AverageHeartRateBpm","MaximumHeartRateBpm","MaximumSpeed",
        "AvgRunCadence","MaxRunCadence","Intensity","StartTime","TriggerMethod"
    ])
    track_writer.writerow([
        "ActivityId","LapNumber","TrackNumber","AltitudeMeters","DistanceMeters",
        "RunCadence","Speed","HeartRateBpm","LatitudeDegrees","LongitudeDegrees","Time"
    ])

    # fill rows
    for activity in root.findall(".//tcx:Activity", ns):
        act_id = activity.find("tcx:Id", ns).text
        sport = activity.get("Sport","Unknown")
        creator = activity.find("tcx:Creator/tcx:Name", ns)
        prod = activity.find("tcx:Creator/tcx:ProductID", ns)
        act_writer.writerow([
            act_id, sport,
            creator.text if creator is not None else "",
            prod.text if prod is not None else ""
        ])

        for i, lap in enumerate(activity.findall("tcx:Lap", ns), start=1):
            lap_writer.writerow([
                act_id, i,
                lap.find("tcx:TotalTimeSeconds",ns).text,
                lap.find("tcx:DistanceMeters",ns).text,
                lap.find("tcx:Calories",ns).text,
                *(lap.find("tcx:AverageHeartRateBpm/tcx:Value",ns).text if lap.find("tcx:AverageHeartRateBpm/tcx:Value",ns)  else "",),
                *(lap.find("tcx:MaximumHeartRateBpm/tcx:Value",ns).text if lap.find("tcx:MaximumHeartRateBpm/tcx:Value",ns) else "",),
                *(lap.find("tcx:MaximumSpeed",ns).text if lap.find("tcx:MaximumSpeed",ns) else "",),
                *(lap.find(".//tcx:Extensions/tcx:LX/tcx:AvgRunCadence",ns).text if lap.find(".//tcx:Extensions/tcx:LX/tcx:AvgRunCadence",ns) else "",),
                *(lap.find(".//tcx:Extensions/tcx:LX/tcx:MaxRunCadence",ns).text if lap.find(".//tcx:Extensions/tcx:LX/tcx:MaxRunCadence",ns) else "",),
                lap.find("tcx:Intensity",ns).text,
                lap.get("StartTime",""),
                lap.find("tcx:TriggerMethod",ns).text
            ])

            for j, tp in enumerate(lap.findall(".//tcx:Trackpoint",ns), start=1):
                track_writer.writerow([
                    act_id, i, j,
                    *(tp.find("tcx:AltitudeMeters",ns).text if tp.find("tcx:AltitudeMeters",ns) else "",),
                    *(tp.find("tcx:DistanceMeters",ns).text if tp.find("tcx:DistanceMeters",ns) else "",),
                    *(tp.find(".//tcx:Extensions/ext:TPX/ext:RunCadence",ns).text if tp.find(".//tcx:Extensions/ext:TPX/ext:RunCadence",ns) else "",),
                    *(tp.find(".//tcx:Extensions/ext:TPX/ext:Speed",ns).text if tp.find(".//tcx:Extensions/ext:TPX/ext:Speed",ns) else "",),
                    *(tp.find("tcx:HeartRateBpm/tcx:Value",ns).text if tp.find("tcx:HeartRateBpm/tcx:Value",ns) else "",),
                    *(tp.find("tcx:Position/tcx:LatitudeDegrees",ns).text if tp.find("tcx:Position/tcx:LatitudeDegrees",ns) else "",),
                    *(tp.find("tcx:Position/tcx:LongitudeDegrees",ns).text if tp.find("tcx:Position/tcx:LongitudeDegrees",ns) else "",),
                    *(tp.find("tcx:Time",ns).text if tp.find("tcx:Time",ns) else "",)
                ])

    # return byte-encoded CSVs
    return (
        act_buf.getvalue().encode('utf-8'),
        lap_buf.getvalue().encode('utf-8'),
        track_buf.getvalue().encode('utf-8')
    )

# --- 2) Build Streamlit UI ---
def main():
    st.title("TCX → CSV Converter")

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
            "📥 Download tracks.csv",
            data=tracks_csv,
            file_name="tracks.csv",
            mime="text/csv",
        )

if __name__ == "__main__":
    main()
