# Diagrams Workflow

This folder contains the architecture diagrams for our project.  
The diagrams are maintained in **Draw.io (`.drawio` files)** and automatically exported to **SVG files** via GitHub Actions.

## Update Process

1. **Edit the diagram** in [draw.io](https://app.diagrams.net/?src=about#HSheikoh%2FREnergies_efficiency_prediction%2Fmain%2Fdiagrams%2Farchitecture.drawio#%7B%22pageId%22%3A%22bG0RTmb4xdSiPlx_l64v%22%7D) (`.drawio` file).
2. **Save changes locally** to your repository.
3. **Commit and push** the updated `.drawio` file.
4. **Automation runs**:
   - GitHub Actions detects changes to `.drawio` files.
   - It exports **one `.svg` file per page** in the document.
   - The exported files are placed in `/diagrams/export/`.
   - **Filenames reflect the page names** in the Draw.io document (e.g., `architecture-Frontend.svg`, `architecture-Backend.svg`).

⚠️ **Keep in mind**:  
- If your `.drawio` has multiple pages, you will get multiple `.svg` files.  
- Page names in Draw.io directly determine the filenames of the exported SVGs.

---

## Process Diagram

```mermaid
flowchart LR
    A[Start] -->B[🖊️Edit<br/>diagram<br/>in Draw.io]
    B --> C[💾 Save<br/>changes<br/>locally]
    C --> D[📤 Add/Commit <br/> and Push <br/>to GitHub]
    D --> E[⚙️ Automation<br/>Exports SVG<br/>per page]
    E --> F[📄 README<br/>updated<br/>with SVGs]
    F --> G[END]

    %% Define styles
    classDef manual fill:#f9f,stroke:#333,stroke-width:1px,color:#000;
    classDef auto fill:#bbf,stroke:#333,stroke-width:1px,color:#000;
    classDef legend fill:#eee,stroke:#999,stroke-width:1px,color:#333;

    %% Assign classes
    class B,C,D manual
    class E,F auto

    %% Legend at bottom
    subgraph Legend [Legend]
      L1[🖐️ Manual]:::manual
      L2[⚙️ Automated]:::auto
    end
    Legend:::legend
