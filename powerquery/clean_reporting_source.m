let
    // pSourcePath is a Power Query text parameter pointing to source_messy_reporting.xlsx.
    Workbook = Excel.Workbook(File.Contents(pSourcePath), null, true),
    RawSheet = Workbook{[Item="Raw_Transactions", Kind="Sheet"]}[Data],
    Promoted = Table.PromoteHeaders(RawSheet, [PromoteAllScalars=true]),
    Contract = Table.SelectColumns(
        Promoted,
        {"Record ID", "Period", "Entity", "Amount", "Owner", "Status", "Comment"},
        MissingField.Error
    ),
    TrimmedText = Table.TransformColumns(
        Contract,
        {
            {"Record ID", each Text.Trim(Text.From(_)), type text},
            {"Period", each Text.Trim(Text.From(_)), type text},
            {"Entity", each Text.Upper(Text.Trim(Text.From(_))), type text},
            {"Status", each Text.Upper(Text.Trim(Text.From(_))), type text}
        }
    ),
    AmountText = Table.TransformColumns(
        TrimmedText,
        {{"Amount", each Text.Replace(Text.Replace(Text.Replace(Text.From(_), " EUR", ""), "€", ""), " ", ""), type text}}
    ),
    DecimalNormalised = Table.TransformColumns(
        AmountText,
        {{"Amount", each Text.Replace(_, ",", "."), type text}}
    ),
    Typed = Table.TransformColumnTypes(
        DecimalNormalised,
        {{"Record ID", type text}, {"Period", type text}, {"Entity", type text}, {"Amount", type number}},
        "en-US"
    ),
    ApprovedOnly = Table.SelectRows(Typed, each [Status] = "APPROVED"),
    NonNegativeOnly = Table.SelectRows(ApprovedOnly, each [Amount] >= 0),
    NonBlankKeys = Table.SelectRows(NonNegativeOnly, each [Record ID] <> "" and [Period] <> ""),
    DistinctBusinessKey = Table.Distinct(NonBlankKeys, {"Record ID"})
in
    DistinctBusinessKey
