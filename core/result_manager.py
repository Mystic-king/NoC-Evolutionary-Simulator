from pathlib import Path
import json
import pandas as pd

class ResultManager:
    @staticmethod
    def save_json(run_dir, filename, data):
        p=Path(run_dir)/filename
        p.write_text(json.dumps(data,indent=2,default=str),encoding="utf-8")
        return p

    @staticmethod
    def save_csv(run_dir, filename, rows):
        p=Path(run_dir)/filename
        pd.DataFrame(rows).to_csv(p,index=False)
        return p

    @staticmethod
    def save_pdf(run_dir,title,result,configuration=None):
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Preformatted,Image
        from reportlab.lib.units import inch
        p=Path(run_dir)/"report.pdf"; styles=getSampleStyleSheet()
        story=[Paragraph(title,styles["Title"]),Spacer(1,10),
               Paragraph("Experiment overview",styles["Heading2"]),
               Paragraph("This report summarizes one execution. The exact configuration, machine-readable results, logs and raw histories are stored alongside this PDF.",styles["BodyText"]),
               Spacer(1,10),Paragraph("Methodology",styles["Heading2"]),
               Paragraph(str(result.get("methodology","Refer to the experiment documentation for the algorithm procedure.")),styles["BodyText"]),
               Spacer(1,6),Paragraph("Objective",styles["Heading2"]),
               Paragraph(str(result.get("objective_description","See the experiment configuration and raw results.")),styles["BodyText"]),
               Spacer(1,10),Paragraph("Configuration",styles["Heading2"]),
               Preformatted(json.dumps(configuration or {},indent=2,default=str),styles["Code"]),
               Spacer(1,10),Paragraph("Results",styles["Heading2"])]
        rows=[["Metric","Value"]]
        def add_scalars(prefix,value):
            if isinstance(value,dict):
                for subkey,subvalue in value.items():
                    add_scalars(f"{prefix}.{subkey}" if prefix else str(subkey),subvalue)
            elif isinstance(value,(str,int,float,bool)) or value is None:
                rows.append([str(prefix).replace("_"," ").title(),str(value)])
        for k,v in result.items():
            if k not in ("comparison","methodology","objective_description"):
                add_scalars(str(k),v)
        table=Table(rows,colWidths=[175,315],repeatRows=1)
        table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#243247")),
          ("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),.4,colors.grey),
          ("VALIGN",(0,0),(-1,-1),"TOP"),("PADDING",(0,0),(-1,-1),6)]))
        story += [table,Spacer(1,12),Paragraph("Interpretation and limitations",styles["Heading2"])]
        if "best_distance" in result:
            note=f"The optimizer returned a closed tour with distance {result['best_distance']:.4f}. A heuristic result is not guaranteed to be globally optimal."
        elif "best_fitness" in result:
            note=f"The best objective value reported by this run is {result['best_fitness']}. Compare multiple random seeds and parameter settings."
        elif "validation_accuracy" in result:
            note=f"Held-out accuracy is {result['validation_accuracy']:.4f}; it measures agreement with generated XY-routing labels, not measured hardware performance."
        elif "validation_rmse" in result:
            note=f"Held-out RMSE is {result['validation_rmse']:.5f} for a synthetic target function, not an external real-world dataset."
        elif result.get("backend")=="actual GEM5 executable":
            note="These statistics were collected from the external GEM5 execution. Interpret counters using the selected GEM5/Garnet configuration and simulator version."
        else:
            note="Review the raw histories and saved configuration before interpreting results. Heuristic methods can vary with random seed and parameters."
        story.append(Paragraph(note,styles["BodyText"]))
        if isinstance(result.get("comparison"),list) and result["comparison"]:
            story += [Spacer(1,10),Paragraph("Algorithm comparison",styles["Heading2"])]
            comparison_rows=[["Algorithm","Best objective"]]
            comparison_rows.extend([[str(row.get("algorithm","")),f"{float(row.get('best_fitness',0)):.6f}"] for row in result["comparison"]])
            comparison_table=Table(comparison_rows,colWidths=[175,315],repeatRows=1)
            comparison_table.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#243247")),
                ("TEXTCOLOR",(0,0),(-1,0),colors.white),
                ("GRID",(0,0),(-1,-1),.4,colors.grey),
                ("PADDING",(0,0),(-1,-1),6)]))
            story.append(comparison_table)
        for image_name in ("fitness_convergence.png","tsp_convergence.png","best_route.png","routing_convergence.png","optimized_route.png","cnn_training.png","cnn_accuracy.png","anfis_training.png","gem5_mesh_topology.png","algorithm_comparison.png"):
            image_path=Path(run_dir)/image_name
            if image_path.exists():
                story += [Spacer(1,10),Paragraph(image_name.replace("_"," ").title(),styles["Heading2"]),
                          Image(str(image_path),width=6.2*inch,height=3.9*inch,kind="proportional")]
        SimpleDocTemplate(str(p),pagesize=A4).build(story)
        return p
