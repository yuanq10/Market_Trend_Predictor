import threading
import customtkinter as ctk

from storage.settings_manager import load_settings, save_settings, load_alerts
import ui.theme as T


class _StockPopup:
    """Floating autocomplete window for stock ticker search."""

    def __init__(self, anchor: ctk.CTkEntry, on_select):
        self._anchor = anchor
        self._on_select = on_select
        self._win = None

    def show(self, results: list):
        if not results:
            self.hide()
            return

        if self._win is None or not self._win.winfo_exists():
            self._win = ctk.CTkToplevel(self._anchor)
            self._win.overrideredirect(True)
            self._win.attributes("-topmost", True)
            self._win.configure(fg_color=T.BORDER)

        self._win.deiconify()

        x = self._anchor.winfo_rootx()
        y = self._anchor.winfo_rooty() + self._anchor.winfo_height() + 2
        w = self._anchor.winfo_width()
        item_h = 36
        h = min(len(results) * item_h + 6, 220)
        self._win.geometry(f"{w}x{h}+{x}+{y}")

        for child in self._win.winfo_children():
            child.destroy()

        inner = ctk.CTkScrollableFrame(
            self._win, fg_color=T.CARD,
            scrollbar_button_color=T.BORDER, corner_radius=0
        )
        inner.pack(fill="both", expand=True, padx=1, pady=1)

        for symbol, name in results:
            row = ctk.CTkFrame(inner, fg_color="transparent", corner_radius=4, cursor="hand2")
            row.pack(fill="x", padx=2, pady=1)

            sym_lbl = ctk.CTkLabel(
                row, text=symbol, anchor="w",
                text_color=T.TEXT, font=ctk.CTkFont(size=12, weight="bold"),
                cursor="hand2"
            )
            sym_lbl.pack(side="left", padx=(8, 4), pady=5)

            if name:
                ctk.CTkLabel(
                    row, text=name, anchor="w",
                    text_color=T.TEXT_MUTED, font=ctk.CTkFont(size=11),
                    cursor="hand2"
                ).pack(side="left", padx=(0, 8), pady=5)

            cmd       = lambda e, s=symbol: self._on_select(s)
            hover_in  = lambda e, r=row: r.configure(fg_color=T.BORDER)
            hover_out = lambda e, r=row: r.configure(fg_color="transparent")
            for w in (row, sym_lbl):
                w.bind("<Button-1>", cmd)
                w.bind("<Enter>", hover_in)
                w.bind("<Leave>", hover_out)

    def hide(self):
        if self._win and self._win.winfo_exists():
            self._win.withdraw()

    def destroy(self):
        if self._win and self._win.winfo_exists():
            self._win.destroy()
        self._win = None


class StocksPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self._app = app
        self._popup: _StockPopup | None = None
        self._debounce_id = None
        self._updating_entry = False
        self._selected_ticker: str | None = None
        self._price_thresholds: list[float] = []
        self._build_ui()
        self.bind("<Destroy>", self._on_destroy)

    # ------------------------------------------------------------------
    # Top-level layout
    # ------------------------------------------------------------------
    def _build_ui(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(16, 0))
        ctk.CTkLabel(
            top, text="Stocks",
            font=ctk.CTkFont(size=22, weight="bold"), text_color=T.TEXT
        ).pack(side="left")

        mid = ctk.CTkFrame(self, fg_color="transparent")
        mid.pack(fill="both", expand=True, padx=20, pady=16)

        # Pack right → left so the info panel fills remaining space

        # Far right: Watchlist (220px)
        right_panel = ctk.CTkFrame(
            mid, width=220, fg_color=T.CARD,
            corner_radius=12, border_width=1, border_color=T.BORDER
        )
        right_panel.pack(side="right", fill="y", padx=(10, 0))
        right_panel.pack_propagate(False)
        self._build_watchlist_panel(right_panel)

        # Centre-right: dynamic panel — Add Stock or Price Alerts (240px)
        self._center_panel = ctk.CTkFrame(
            mid, width=240, fg_color=T.CARD,
            corner_radius=12, border_width=1, border_color=T.BORDER
        )
        self._center_panel.pack(side="right", fill="y", padx=(10, 0))
        self._center_panel.pack_propagate(False)

        # Left: Company Info (fills remaining space)
        self._info_panel = ctk.CTkFrame(
            mid, fg_color=T.CARD,
            corner_radius=12, border_width=1, border_color=T.BORDER
        )
        self._info_panel.pack(side="left", fill="both", expand=True)

        self._show_add_mode()
        self._show_info_placeholder()

    # ------------------------------------------------------------------
    # Company Info panel (left, fills)
    # ------------------------------------------------------------------
    def _show_info_placeholder(self):
        for w in self._info_panel.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self._info_panel,
            text="Select a stock from the watchlist\nto view company details.",
            font=ctk.CTkFont(size=13), text_color=T.TEXT_MUTED,
            justify="center"
        ).pack(expand=True)

    def _select_ticker(self, ticker: str):
        """Load company info without touching the centre panel."""
        self._selected_ticker = ticker
        self._fetch_and_show_info(ticker)

    def _fetch_and_show_info(self, ticker: str):
        for w in self._info_panel.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self._info_panel, text=f"Loading {ticker}…",
            font=ctk.CTkFont(size=12), text_color=T.TEXT_MUTED
        ).pack(expand=True)
        threading.Thread(
            target=self._fetch_company_info, args=(ticker,), daemon=True
        ).start()

    def _fetch_company_info(self, ticker: str):
        try:
            import yfinance as yf
            info = yf.Ticker(ticker).info
            self.after(0, lambda: self._render_company_info(ticker, info))
        except Exception as e:
            self.after(0, lambda: self._show_info_error(str(e)))

    def _render_company_info(self, ticker: str, info: dict):
        for w in self._info_panel.winfo_children():
            w.destroy()

        scroll = ctk.CTkScrollableFrame(
            self._info_panel, fg_color="transparent",
            scrollbar_button_color=T.BORDER
        )
        scroll.pack(fill="both", expand=True, padx=16, pady=14)

        # Company name + Set Alert button on the same row
        name = info.get("longName") or info.get("shortName") or ticker
        self._last_info = info

        name_row = ctk.CTkFrame(scroll, fg_color="transparent")
        name_row.pack(fill="x", pady=(0, 2))

        ctk.CTkLabel(
            name_row, text=name, anchor="w", wraplength=380,
            font=ctk.CTkFont(size=20, weight="bold"), text_color=T.TEXT
        ).pack(side="left")

        ctk.CTkButton(
            name_row, text="Set Alert", width=96, height=34, corner_radius=8,
            fg_color=T.ACCENT, hover_color="#79b8ff", text_color="#000000",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="center",
            command=lambda t=ticker: self._load_price_alerts(t)
        ).pack(side="left", padx=(28, 0), pady=(8, 0))

        # Symbol / exchange line
        sub = ticker
        exchange = info.get("exchange") or info.get("fullExchangeName")
        if exchange:
            sub += f"  ·  {exchange}"
        ctk.CTkLabel(
            scroll, text=sub, anchor="w",
            font=ctk.CTkFont(size=12), text_color=T.TEXT_MUTED
        ).pack(anchor="w", pady=(0, 12))

        ctk.CTkFrame(scroll, height=1, fg_color=T.BORDER).pack(fill="x", pady=(0, 12))

        # Helper to format values
        def fmt_cap(v):
            if v is None:
                return "—"
            if v >= 1e12:
                return f"${v/1e12:.2f}T"
            if v >= 1e9:
                return f"${v/1e9:.2f}B"
            if v >= 1e6:
                return f"${v/1e6:.2f}M"
            return f"${v:,.0f}"

        def fmt_pct(v):
            return f"{v*100:.2f}%" if v is not None else "—"

        def fmt_num(v):
            return f"{v:,}" if v is not None else "—"

        def fmt_val(v):
            return str(v) if v is not None else "—"

        metrics = [
            ("Sector",         fmt_val(info.get("sector"))),
            ("Industry",       fmt_val(info.get("industry"))),
            ("Market Cap",     fmt_cap(info.get("marketCap"))),
            ("Volume",         fmt_num(info.get("regularMarketVolume") or info.get("volume"))),
            ("52w High",       f"${info['fiftyTwoWeekHigh']}" if info.get("fiftyTwoWeekHigh") else "—"),
            ("52w Low",        f"${info['fiftyTwoWeekLow']}"  if info.get("fiftyTwoWeekLow")  else "—"),
            ("P/E (trailing)", fmt_val(info.get("trailingPE"))),
            ("P/E (forward)",  fmt_val(info.get("forwardPE"))),
            ("Div Yield",      fmt_pct(info.get("dividendYield"))),
            ("Beta",           fmt_val(info.get("beta"))),
            ("Employees",      fmt_num(info.get("fullTimeEmployees"))),
            ("Country",        fmt_val(info.get("country"))),
            ("City",           fmt_val(info.get("city"))),
            ("Website",        (info.get("website") or "—").replace("https://", "").replace("http://", "").rstrip("/")),
        ]

        # 2-column grid
        grid = ctk.CTkFrame(scroll, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 12))
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        for idx, (label, value) in enumerate(metrics):
            card = ctk.CTkFrame(grid, fg_color=T.BG, corner_radius=8,
                                border_width=1, border_color=T.BORDER)
            card.grid(row=idx // 2, column=idx % 2, sticky="ew",
                      padx=3, pady=3)
            ctk.CTkLabel(
                card, text=label, anchor="w",
                font=ctk.CTkFont(size=10), text_color=T.TEXT_MUTED
            ).pack(anchor="w", padx=8, pady=(5, 0))
            ctk.CTkLabel(
                card, text=value, anchor="w", wraplength=350,
                font=ctk.CTkFont(size=12, weight="bold"), text_color=T.TEXT
            ).pack(anchor="w", padx=8, pady=(1, 6))

        # Business summary
        summary = info.get("longBusinessSummary")
        if summary:
            ctk.CTkFrame(scroll, height=1, fg_color=T.BORDER).pack(fill="x", pady=(4, 10))
            ctk.CTkLabel(
                scroll, text="About", anchor="w",
                font=ctk.CTkFont(size=14, weight="bold"), text_color=T.TEXT
            ).pack(anchor="w", pady=(0, 6))
            summary_lbl = ctk.CTkLabel(
                scroll, text=summary, anchor="w", justify="left",
                wraplength=600,
                font=ctk.CTkFont(size=11), text_color=T.TEXT_MUTED
            )
            summary_lbl.pack(anchor="w", fill="x")

            def _apply_wrap(w, lbl=summary_lbl):
                if lbl.winfo_exists():
                    lbl.configure(wraplength=max(200, w - 70))

            # Set wraplength once after layout settles (handles already-maximized case)
            self.after(80, lambda: _apply_wrap(self._info_panel.winfo_width()))

            _resize_id = [None]
            def _on_panel_resize(event, lbl=summary_lbl, rid=_resize_id):
                if rid[0]:
                    self.after_cancel(rid[0])
                captured_w = event.width
                rid[0] = self.after(60, lambda: _apply_wrap(captured_w))
            self._info_panel.bind("<Configure>", _on_panel_resize)

    def _show_info_error(self, msg: str):
        for w in self._info_panel.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self._info_panel, text=f"Failed to load info:\n{msg}",
            font=ctk.CTkFont(size=11), text_color=T.DANGER, justify="center"
        ).pack(expand=True)

    # ------------------------------------------------------------------
    # Centre panel — Add Stock mode
    # ------------------------------------------------------------------
    def _show_add_mode(self):
        self._selected_ticker = None
        if self._popup:
            self._popup.hide()
        for w in self._center_panel.winfo_children():
            w.destroy()

        ctk.CTkLabel(
            self._center_panel, text="Add Stock",
            font=ctk.CTkFont(size=18, weight="bold"), text_color=T.TEXT
        ).pack(pady=(14, 8), padx=14, anchor="w")

        ctk.CTkFrame(self._center_panel, height=1, fg_color=T.BORDER).pack(fill="x", padx=14)

        content = ctk.CTkFrame(self._center_panel, fg_color="transparent")
        content.pack(fill="x", padx=14, pady=14)

        ctk.CTkLabel(
            content, text="Search ticker or company", anchor="w",
            text_color=T.TEXT_MUTED, font=ctk.CTkFont(size=11)
        ).pack(anchor="w", pady=(0, 4))

        self._ticker_var = ctk.StringVar()
        self._entry_ticker = ctk.CTkEntry(
            content, textvariable=self._ticker_var,
            placeholder_text="e.g. AAPL or Apple…",
            height=34, corner_radius=8,
            fg_color=T.BG, border_color=T.BORDER,
            text_color=T.TEXT, placeholder_text_color=T.TEXT_MUTED
        )
        self._entry_ticker.pack(fill="x")
        self._entry_ticker.bind("<Return>", lambda _: self._on_add())
        self._entry_ticker.bind(
            "<FocusOut>",
            lambda e: self.after(160, lambda: self._popup.hide() if self._popup else None)
        )
        self._ticker_var.trace_add("write", self._on_ticker_type)
        self._popup = _StockPopup(self._entry_ticker, self._on_select_suggestion)

        self._lbl_msg = ctk.CTkLabel(
            content, text="", font=ctk.CTkFont(size=11), text_color=T.TEXT_MUTED,
            wraplength=200
        )
        self._lbl_msg.pack(anchor="w", pady=(8, 0))

        ctk.CTkButton(
            content, text="Add to Watchlist", height=34, corner_radius=8,
            fg_color=T.ACCENT, hover_color="#79b8ff", text_color="#000000",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._on_add
        ).pack(fill="x", pady=(8, 0))

    # ------------------------------------------------------------------
    # Info panel — Price Alerts view
    # ------------------------------------------------------------------
    def _load_price_alerts(self, ticker: str):
        self._selected_ticker = ticker
        for w in self._info_panel.winfo_children():
            w.destroy()

        scroll = ctk.CTkScrollableFrame(
            self._info_panel, fg_color="transparent",
            scrollbar_button_color=T.BORDER
        )
        scroll.pack(fill="both", expand=True, padx=16, pady=14)

        # Header: back button + title
        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, 2))

        ctk.CTkButton(
            header, text="← Back", width=70, height=28, corner_radius=8,
            fg_color=T.BORDER, hover_color=T.CARD,
            text_color=T.TEXT, font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda t=ticker: self._render_company_info(
                t, getattr(self, "_last_info", {}))
        ).pack(side="left")

        ctk.CTkLabel(
            header, text="Price Alerts",
            font=ctk.CTkFont(size=18, weight="bold"), text_color=T.TEXT
        ).pack(side="left", padx=(10, 0))

        ctk.CTkLabel(
            scroll, text=f"Stock code: {ticker}", anchor="w",
            font=ctk.CTkFont(size=15, weight="bold"), text_color=T.TEXT
        ).pack(anchor="w", pady=(2, 0))

        ctk.CTkFrame(scroll, height=1, fg_color=T.BORDER).pack(
            fill="x", pady=(10, 12)
        )

        ctk.CTkLabel(
            scroll,
            text="Alert fires when the stock price crosses any of these values.",
            anchor="w", text_color=T.TEXT_MUTED, font=ctk.CTkFont(size=11),
            justify="left"
        ).pack(anchor="w", pady=(0, 10))

        settings = load_settings()
        self._price_thresholds = list(
            settings.get("stock_thresholds", {}).get(ticker, [])
        )

        self._threshold_list_frame = ctk.CTkFrame(scroll, fg_color=T.BG, corner_radius=6)
        self._threshold_list_frame.pack(fill="x", pady=(0, 8))
        self._render_price_thresholds(ticker)

        add_row = ctk.CTkFrame(scroll, fg_color="transparent")
        add_row.pack(fill="x")

        self._price_entry = ctk.CTkEntry(
            add_row, height=28, corner_radius=6,
            fg_color=T.BG, border_color=T.BORDER, text_color=T.TEXT,
            placeholder_text="price", placeholder_text_color=T.TEXT_MUTED
        )
        self._price_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self._price_entry.bind("<Return>", lambda e: self._on_add_price_threshold(ticker))

        ctk.CTkButton(
            add_row, text="+ Add", width=60, height=28, corner_radius=6,
            fg_color=T.ACCENT, hover_color="#79b8ff", text_color="#000000",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda: self._on_add_price_threshold(ticker)
        ).pack(side="left")

    def _render_price_thresholds(self, ticker: str):
        for w in self._threshold_list_frame.winfo_children():
            w.destroy()

        if not self._price_thresholds:
            ctk.CTkLabel(
                self._threshold_list_frame,
                text="No price alerts set", anchor="w",
                text_color=T.TEXT_MUTED, font=ctk.CTkFont(size=10)
            ).pack(anchor="w", padx=8, pady=6)
        else:
            for val in sorted(self._price_thresholds):
                row = ctk.CTkFrame(self._threshold_list_frame, fg_color="transparent")
                row.pack(fill="x", padx=6, pady=2)
                ctk.CTkLabel(
                    row, text=f"${val:g}", anchor="w",
                    text_color=T.TEXT, font=ctk.CTkFont(size=12)
                ).pack(side="left", padx=4)
                ctk.CTkButton(
                    row, text="×", width=20, height=20, corner_radius=4,
                    fg_color="transparent", hover_color=T.DANGER,
                    text_color=T.TEXT_MUTED, font=ctk.CTkFont(size=10),
                    command=lambda v=val: self._on_remove_price_threshold(ticker, v)
                ).pack(side="right")

    def _on_add_price_threshold(self, ticker: str):
        try:
            val = float(self._price_entry.get().strip())
        except ValueError:
            return
        if val not in self._price_thresholds:
            self._price_thresholds.append(val)
        self._price_entry.delete(0, "end")
        self._save_price_thresholds(ticker)
        self._render_price_thresholds(ticker)

    def _on_remove_price_threshold(self, ticker: str, val: float):
        if val in self._price_thresholds:
            self._price_thresholds.remove(val)
        self._save_price_thresholds(ticker)
        self._render_price_thresholds(ticker)

    def _save_price_thresholds(self, ticker: str):
        settings = load_settings()
        thresholds = settings.get("stock_thresholds", {})
        thresholds[ticker] = self._price_thresholds
        settings["stock_thresholds"] = thresholds
        save_settings(settings)
        self._refresh_stocks_list()

    # ------------------------------------------------------------------
    # Watchlist panel (right, 220px)
    # ------------------------------------------------------------------
    def _build_watchlist_panel(self, panel):
        ctk.CTkLabel(
            panel, text="Watchlist",
            font=ctk.CTkFont(size=18, weight="bold"), text_color=T.TEXT
        ).pack(pady=(14, 8), padx=12, anchor="w")

        self._stocks_scroll = ctk.CTkScrollableFrame(
            panel, fg_color="transparent", scrollbar_button_color=T.BORDER
        )
        self._stocks_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self._refresh_stocks_list()

    def on_show(self):
        self._refresh_stocks_list()

    def on_hide(self):
        if getattr(self, "_popup", None):
            self._popup.hide()

    def _refresh_stocks_list(self):
        for w in self._stocks_scroll.winfo_children():
            w.destroy()

        settings = load_settings()
        stocks = settings.get("stocks", [])
        stock_thresholds = settings.get("stock_thresholds", {})

        if not stocks:
            ctk.CTkLabel(
                self._stocks_scroll,
                text="No stocks added yet.",
                font=ctk.CTkFont(size=12), text_color=T.TEXT_MUTED
            ).pack(pady=20)
            return

        alerts_data = load_alerts()
        stats = alerts_data.get("stats", {})

        for ticker in stocks:
            n_alerts = len(stock_thresholds.get(ticker, []))
            self._make_watchlist_item(ticker, stats.get(ticker, {}), n_alerts)

    def _make_watchlist_item(self, ticker: str, stat: dict, n_alerts: int):
        item = ctk.CTkFrame(
            self._stocks_scroll, fg_color=T.BG,
            corner_radius=8, border_width=1, border_color=T.BORDER
        )
        item.pack(fill="x", pady=3)

        # Top row: ticker (clickable) + alert badge + delete button
        top_row = ctk.CTkFrame(item, fg_color="transparent")
        top_row.pack(fill="x", padx=8, pady=(6, 2))

        ctk.CTkButton(
            top_row, text="✕", width=20, height=20, corner_radius=4,
            fg_color="transparent", hover_color=T.DANGER,
            text_color=T.TEXT_MUTED, font=ctk.CTkFont(size=10),
            command=lambda t=ticker: self._on_remove(t)
        ).pack(side="right")

        if n_alerts > 0:
            ctk.CTkLabel(
                top_row, text=f"🔔{n_alerts}",
                font=ctk.CTkFont(size=10), text_color=T.WARNING
            ).pack(side="right", padx=(0, 4))

        ticker_btn = ctk.CTkButton(
            top_row, text=ticker, anchor="w",
            fg_color="transparent", hover_color=T.CARD,
            text_color=T.TEXT, font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda t=ticker: self._select_ticker(t)
        )
        ticker_btn.pack(side="left")

        # Bottom row: price + change %
        close = stat.get("close")
        change = stat.get("change_pct")
        if close is not None or change is not None:
            bot_row = ctk.CTkFrame(item, fg_color="transparent")
            bot_row.pack(fill="x", padx=8, pady=(0, 6))
            if close is not None:
                ctk.CTkLabel(
                    bot_row, text=f"${close}",
                    font=ctk.CTkFont(size=11), text_color=T.TEXT_MUTED
                ).pack(side="left", padx=(6, 0))
            if change is not None:
                color = T.SUCCESS if change >= 0 else T.DANGER
                sign = "+" if change >= 0 else ""
                ctk.CTkLabel(
                    bot_row, text=f"{sign}{change:.2f}%",
                    font=ctk.CTkFont(size=11, weight="bold"), text_color=color
                ).pack(side="right")
        else:
            ctk.CTkFrame(item, fg_color="transparent", height=4).pack()

    # ------------------------------------------------------------------
    # Add / Remove stock
    # ------------------------------------------------------------------
    def _on_add(self):
        ticker = self._entry_ticker.get().strip().upper()
        if not ticker:
            return
        settings = load_settings()
        stocks = settings.get("stocks", [])
        if ticker in stocks:
            self._lbl_msg.configure(
                text=f"{ticker} already in watchlist.", text_color=T.WARNING
            )
            return
        if self._popup:
            self._popup.hide()
        self._lbl_msg.configure(text=f"Checking {ticker}…", text_color=T.TEXT_MUTED)
        threading.Thread(target=self._validate_and_add, args=(ticker,), daemon=True).start()

    def _validate_and_add(self, ticker: str):
        try:
            import yfinance as yf
            info = yf.Ticker(ticker).info
            valid = bool(info.get("quoteType") and info.get("symbol"))
        except Exception:
            valid = False

        if valid:
            self.after(0, lambda: self._do_add(ticker))
        else:
            self.after(0, lambda: self._lbl_msg.configure(
                text=f'"{ticker}" is not a recognised symbol.',
                text_color=T.DANGER
            ))

    def _do_add(self, ticker: str):
        settings = load_settings()
        stocks = settings.get("stocks", [])
        if ticker not in stocks:
            stocks.append(ticker)
            settings["stocks"] = stocks
            save_settings(settings)
        self._entry_ticker.delete(0, "end")
        self._lbl_msg.configure(text=f"Added {ticker}.", text_color=T.SUCCESS)
        self._refresh_stocks_list()

    def _on_remove(self, ticker: str):
        settings = load_settings()
        stocks = settings.get("stocks", [])
        if ticker in stocks:
            stocks.remove(ticker)
        thresholds = settings.get("stock_thresholds", {})
        thresholds.pop(ticker, None)
        settings["stocks"] = stocks
        settings["stock_thresholds"] = thresholds
        save_settings(settings)
        if self._selected_ticker == ticker:
            self._show_add_mode()
            self._show_info_placeholder()
        else:
            self._refresh_stocks_list()

    # ------------------------------------------------------------------
    # Autocomplete
    # ------------------------------------------------------------------
    def _on_destroy(self, event):
        if event.widget is self and self._popup:
            self._popup.destroy()

    def _on_ticker_type(self, *_):
        if self._updating_entry:
            return
        query = self._ticker_var.get().strip()
        if not query:
            if self._popup:
                self._popup.hide()
            return
        if self._debounce_id:
            self.after_cancel(self._debounce_id)
        self._debounce_id = self.after(350, lambda q=query: self._run_search(q))

    def _run_search(self, query: str):
        threading.Thread(target=self._search_stocks, args=(query,), daemon=True).start()

    def _search_stocks(self, query: str):
        try:
            import yfinance as yf
            results = yf.Search(query, max_results=8, news_count=0).quotes
            suggestions = []
            for r in results:
                symbol = r.get("symbol", "")
                name = r.get("shortname") or r.get("longname") or ""
                if symbol:
                    suggestions.append((symbol, name))
            self.after(0, lambda: self._popup.show(suggestions) if self._popup else None)
        except Exception:
            pass

    def _on_select_suggestion(self, symbol: str):
        self._updating_entry = True
        self._ticker_var.set(symbol.upper())
        self._updating_entry = False
        if self._popup:
            self._popup.hide()
