%%{init: {"theme":"default", "themeVariables": {
    "primaryColor": "#f0f0f0",
    "edgeLabelBackground":"#ffffff",
    "fontSize":"16px",
    "nodeTextColor":"#1F2937"
}}}%%
flowchart TD
    %% Data Source
    A1(["<b>🛰️ Twitter API</b><br/>(منبع داده)"])
    style A1 fill:#89CFF0,stroke:#005f73,stroke-width:2px,color:#001219

    %% Extraction & Loading
    B1(["<b>🛠️ Airbyte</b><br/>(استخراج و بارگذاری)"])
    style B1 fill:#FFD6A5,stroke:#fb8500,stroke-width:2px,color:#6F1D1B

    C1(["<b>🗄️ Staging DB</b><br/>(Postgres/BigQuery - داده خام)"])
    style C1 fill:#FFE066,stroke:#ffb703,stroke-width:2px,color:#6F1D1B

    %% Transformation
    D1(["<b>🔧 dbt Models</b><br/>(مدل‌سازی و پاکسازی داده)"])
    style D1 fill:#B9FBC0,stroke:#38B000,stroke-width:2px,color:#004B23

    %% Data Warehouse
    E1(["<b>🏛️ Analytics DB</b><br/>(جداول تحلیلی - داده پاک)"])
    style E1 fill:#90E0EF,stroke:#0077b6,stroke-width:2px,color:#003566

    %% Visualization
    F1(["<b>📊 Metabase Dashboards</b><br/>(بصری‌سازی و گزارشات)"])
    style F1 fill:#FFB3C1,stroke:#ff006e,stroke-width:2px,color:#800F2F

    %% Orchestration
    G1(["<b>🚀 Apache Airflow</b><br/>(زمان‌بندی، ارکستراسیون، مانیتورینگ)"])
    style G1 fill:#D0BFFF,stroke:#7B2CBF,stroke-width:2px,color:#240046

    %% Data Flow
    A1 --> B1
    B1 --> C1
    C1 --> D1
    D1 --> E1
    E1 --> F1

    %% Orchestration Arrows (dashed)
    G1 -.-> A1
    G1 -.-> B1
    G1 -.-> C1
    G1 -.-> D1
    G1 -.-> E1
    G1 -.-> F1

    %% Grouping
    subgraph "🌐 Data Source"
        A1
    end

    subgraph "⚡ Extraction & Loading (EL)"
        B1
        C1
    end

    subgraph "🔄 Transformation (T)"
        D1
    end

    subgraph "🏛️ Analytics & Storage"
        E1
    end

    subgraph "📊 Business Intelligence"
        F1
    end

    subgraph "🛫 Orchestration"
        G1
    end
