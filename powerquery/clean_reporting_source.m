let
    // pSourcePath is a Power Query text parameter pointing to source_messy_reporting.xlsx.
    Workbook = Excel.Workbook(File.Contents(pSourcePath), null, true),

    RawSheet = Workbook{[Item="Raw_Transactions", Kind="Sheet"]}[Data],
    RawPromoted = Table.PromoteHeaders(RawSheet, [PromoteAllScalars=true]),
    Contract = Table.SelectColumns(
        RawPromoted,
        {"Record ID", "Period", "Entity", "Amount", "Owner", "Status", "Comment"},
        MissingField.Error
    ),
    WithSourceRow = Table.AddIndexColumn(Contract, "Source Row", 2, 1, Int64.Type),
    NormalisedText = Table.TransformColumns(
        WithSourceRow,
        {
            {"Record ID", each Text.Trim(Text.From(_)), type text},
            {"Period", each Text.Trim(Text.From(_)), type text},
            {"Entity", each Text.Upper(Text.Trim(Text.From(_))), type text},
            {"Owner", each Text.Trim(Text.From(_)), type text},
            {"Status", each Text.Upper(Text.Trim(Text.From(_))), type text}
        }
    ),
    AmountText = Table.AddColumn(
        NormalisedText,
        "Parsed Amount",
        each
            let
                Clean = Text.Replace(
                    Text.Replace(
                        Text.Replace(Text.From([Amount]), " EUR", ""),
                        "€",
                        ""
                    ),
                    " ",
                    ""
                ),
                DecimalNormalised = Text.Replace(Clean, ",", ".")
            in
                try Number.FromText(DecimalNormalised, "en-US") otherwise null,
        type number
    ),

    MapSheet = Workbook{[Item="Entity_Map", Kind="Sheet"]}[Data],
    MapPromoted = Table.PromoteHeaders(MapSheet, [PromoteAllScalars=true]),
    MapContract = Table.SelectColumns(
        MapPromoted,
        {"Raw Entity", "Canonical Entity"},
        MissingField.Error
    ),
    MapNormalised = Table.TransformColumns(
        MapContract,
        {
            {"Raw Entity", each Text.Upper(Text.Trim(Text.From(_))), type text},
            {"Canonical Entity", each Text.Trim(Text.From(_)), type text}
        }
    ),
    JoinedMap = Table.NestedJoin(
        AmountText,
        {"Entity"},
        MapNormalised,
        {"Raw Entity"},
        "EntityMap",
        JoinKind.LeftOuter
    ),
    ExpandedMap = Table.ExpandTableColumn(
        JoinedMap,
        "EntityMap",
        {"Canonical Entity"},
        {"Canonical Entity"}
    ),

    Reportable = Table.SelectRows(
        ExpandedMap,
        each
            [Status] = "APPROVED"
            and [Record ID] <> ""
            and [Period] <> ""
            and [Parsed Amount] <> null
            and [Parsed Amount] >= 0
            and [Canonical Entity] <> null
    ),
    DistinctBusinessKey = Table.Distinct(Reportable, {"Record ID"}),
    Selected = Table.SelectColumns(
        DistinctBusinessKey,
        {
            "Record ID",
            "Period",
            "Canonical Entity",
            "Parsed Amount",
            "Owner",
            "Status",
            "Source Row"
        }
    ),
    Renamed = Table.RenameColumns(
        Selected,
        {
            {"Record ID", "record_id"},
            {"Period", "period"},
            {"Canonical Entity", "entity"},
            {"Parsed Amount", "amount"},
            {"Owner", "owner"},
            {"Status", "status"},
            {"Source Row", "source_row"}
        }
    )
in
    Renamed
