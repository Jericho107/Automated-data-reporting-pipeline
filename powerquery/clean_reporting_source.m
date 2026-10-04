let
    Source = Excel.CurrentWorkbook(){[Name="Raw_Transactions"]}[Content],
    TrimmedText = Table.TransformColumns(
        Source,
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
        {{"Record ID", type text}, {"Period", type text}, {"Entity", type text}, {"Amount", type number}}
    ),
    ApprovedOnly = Table.SelectRows(Typed, each [Status] = "APPROVED"),
    NonNegativeOnly = Table.SelectRows(ApprovedOnly, each [Amount] >= 0),
    NonBlankKeys = Table.SelectRows(NonNegativeOnly, each [Record ID] <> "" and [Period] <> ""),
    DistinctBusinessKey = Table.Distinct(NonBlankKeys, {"Record ID"})
in
    DistinctBusinessKey
