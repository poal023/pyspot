from util.util import *
from hotspot_config.hotspot_config import HotSpotConfig

class PackageRC:
    def __init__(self, cfg : HotSpotConfig):
        # Primary path - lateral R
        self.r_sp1_x: float = 0.0
        self.r_sp1_y: float = 0.0
        self.r_hs1_x: float = 0.0
        self.r_hs1_y: float = 0.0
        self.r_hs2_x: float = 0.0
        self.r_hs2_y: float = 0.0
        self.r_hs: float = 0.0
        
        # Primary path - vertical R
        self.r_sp_per_x: float = 0.0
        self.r_sp_per_y: float = 0.0
        self.r_hs_c_per_x: float = 0.0
        self.r_hs_c_per_y: float = 0.0
        self.r_hs_per: float = 0.0
        
        # Primary path - vertical C
        self.c_sp_per_x: float = 0.0
        self.c_sp_per_y: float = 0.0
        self.c_hs_c_per_x: float = 0.0
        self.c_hs_c_per_y: float = 0.0
        self.c_hs_per: float = 0.0
        
        # Primary path - ambient R and C
        self.r_amb_c_per_x: float = 0.0
        self.c_amb_c_per_x: float = 0.0
        self.r_amb_c_per_y: float = 0.0
        self.c_amb_c_per_y: float = 0.0
        self.r_amb_per: float = 0.0
        self.c_amb_per: float = 0.0
        
        # Secondary path - lateral R
        self.r_sub1_x: float = 0.0
        self.r_sub1_y: float = 0.0
        self.r_solder1_x: float = 0.0
        self.r_solder1_y: float = 0.0
        self.r_pcb1_x: float = 0.0
        self.r_pcb1_y: float = 0.0
        self.r_pcb2_x: float = 0.0
        self.r_pcb2_y: float = 0.0
        self.r_pcb: float = 0.0
        
        # Secondary path - vertical R
        self.r_sub_per_x: float = 0.0
        self.r_sub_per_y: float = 0.0
        self.r_solder_per_x: float = 0.0
        self.r_solder_per_y: float = 0.0
        self.r_pcb_c_per_x: float = 0.0
        self.r_pcb_c_per_y: float = 0.0
        self.r_pcb_per: float = 0.0
        
        # Secondary path - vertical C
        self.c_sub_per_x: float = 0.0
        self.c_sub_per_y: float = 0.0
        self.c_solder_per_x: float = 0.0
        self.c_solder_per_y: float = 0.0
        self.c_pcb_c_per_x: float = 0.0
        self.c_pcb_c_per_y: float = 0.0
        self.c_pcb_per: float = 0.0
        
        # Secondary path - ambient R and C
        self.r_amb_sec_c_per_x: float = 0.0
        self.c_amb_sec_c_per_x: float = 0.0
        self.r_amb_sec_c_per_y: float = 0.0
        self.c_amb_sec_c_per_y: float = 0.0
        self.r_amb_sec_per: float = 0.0
        self.c_amb_sec_per: float = 0.0

        self.populate_R(cfg)
        self.populate_C(cfg)

    def populate_R(self, config):
        """Internal method to populate thermal resistances."""
        cfg = config._cfg
        width = config._flp_cfg._width
        height = config._flp_cfg._height

        s_sp = cfg["s_spreader"]
        t_sp = cfg["t_spreader"]
        s_sk = cfg["s_sink"]
        t_sk = cfg["t_sink"]
        r_cv = cfg["r_convec"]
        k_sk = cfg["k_sink"]
        k_sp = cfg["k_spreader"]
        s_sub = cfg["s_sub"]
        t_sub = cfg["t_sub"]
        s_sol = cfg["s_solder"]
        t_sol = cfg["t_solder"]
        s_pcb = cfg["s_pcb"]
        t_pcb = cfg["t_pcb"]
        r_cv_sec = cfg.get("r_convec_sec", 1.0)

        # Primary path R
        self.r_sp1_x = get_resistance(k_sp, (s_sp - width) / 4.0, (s_sp + 3 * height) / 4.0 * t_sp)
        self.r_sp1_y = get_resistance(k_sp, (s_sp - height) / 4.0, (s_sp + 3 * width) / 4.0 * t_sp)
        self.r_hs1_x = get_resistance(k_sk, (s_sp - width) / 4.0, (s_sp + 3 * height) / 4.0 * t_sk)
        self.r_hs1_y = get_resistance(k_sk, (s_sp - height) / 4.0, (s_sp + 3 * width) / 4.0 * t_sk)
        self.r_hs2_x = get_resistance(k_sk, (s_sp - width) / 4.0, (3 * s_sp + height) / 4.0 * t_sk)
        self.r_hs2_y = get_resistance(k_sk, (s_sp - height) / 4.0, (3 * s_sp + width) / 4.0 * t_sk)
        self.r_hs = get_resistance(k_sk, (s_sk - s_sp) / 4.0, (s_sk + 3 * s_sp) / 4.0 * t_sk)

        self.r_sp_per_x = get_resistance(k_sp, t_sp, (s_sp + height) * (s_sp - width) / 4.0)
        self.r_sp_per_y = get_resistance(k_sp, t_sp, (s_sp + width) * (s_sp - height) / 4.0)
        self.r_hs_c_per_x = get_resistance(k_sk, t_sk, (s_sp + height) * (s_sp - width) / 4.0)
        self.r_hs_c_per_y = get_resistance(k_sk, t_sk, (s_sp + width) * (s_sp - height) / 4.0)
        self.r_hs_per = get_resistance(k_sk, t_sk, (s_sk * s_sk - s_sp * s_sp) / 4.0)

        self.r_amb_c_per_x = r_cv * (s_sk * s_sk) / ((s_sp + height) * (s_sp - width) / 4.0)
        self.r_amb_c_per_y = r_cv * (s_sk * s_sk) / ((s_sp + width) * (s_sp - height) / 4.0)
        self.r_amb_per = r_cv * (s_sk * s_sk) / ((s_sk * s_sk - s_sp * s_sp) / 4.0)

        # Secondary path R
        self.r_sub1_x = get_resistance(K_SUB, (s_sub - width) / 4.0, (s_sub + 3 * height) / 4.0 * t_sub)
        self.r_sub1_y = get_resistance(K_SUB, (s_sub - height) / 4.0, (s_sub + 3 * width) / 4.0 * t_sub)
        self.r_solder1_x = get_resistance(K_SOLDER, (s_sol - width) / 4.0, (s_sol + 3 * height) / 4.0 * t_sol)
        self.r_solder1_y = get_resistance(K_SOLDER, (s_sol - height) / 4.0, (s_sol + 3 * width) / 4.0 * t_sol)
        self.r_pcb1_x = get_resistance(K_PCB, (s_sol - width) / 4.0, (s_sol + 3 * height) / 4.0 * t_pcb)
        self.r_pcb1_y = get_resistance(K_PCB, (s_sol - height) / 4.0, (s_sol + 3 * width) / 4.0 * t_pcb)
        self.r_pcb2_x = get_resistance(K_PCB, (s_sol - width) / 4.0, (3 * s_sol + height) / 4.0 * t_pcb)
        self.r_pcb2_y = get_resistance(K_PCB, (s_sol - height) / 4.0, (3 * s_sol + width) / 4.0 * t_pcb)
        self.r_pcb = get_resistance(K_PCB, (s_pcb - s_sol) / 4.0, (s_pcb + 3 * s_sol) / 4.0 * t_pcb)

        self.r_sub_per_x = get_resistance(K_SUB, t_sub, (s_sub + height) * (s_sub - width) / 4.0)
        self.r_sub_per_y = get_resistance(K_SUB, t_sub, (s_sub + width) * (s_sub - height) / 4.0)
        self.r_solder_per_x = get_resistance(K_SOLDER, t_sol, (s_sol + height) * (s_sol - width) / 4.0)
        self.r_solder_per_y = get_resistance(K_SOLDER, t_sol, (s_sol + width) * (s_sol - height) / 4.0)
        self.r_pcb_c_per_x = get_resistance(K_PCB, t_pcb, (s_sol + height) * (s_sol - width) / 4.0)
        self.r_pcb_c_per_y = get_resistance(K_PCB, t_pcb, (s_sol + width) * (s_sol - height) / 4.0)
        self.r_pcb_per = get_resistance(K_PCB, t_pcb, (s_pcb * s_pcb - s_sol * s_sol) / 4.0)

        self.r_amb_sec_c_per_x = r_cv_sec * (s_pcb * s_pcb) / ((s_sol + height) * (s_sol - width) / 4.0)
        self.r_amb_sec_c_per_y = r_cv_sec * (s_pcb * s_pcb) / ((s_sol + width) * (s_sol - height) / 4.0)
        self.r_amb_sec_per = r_cv_sec * (s_pcb * s_pcb) / ((s_pcb * s_pcb - s_sol * s_sol) / 4.0)

    def populate_C(self, config):
        """Internal method to populate thermal capacitances."""
        # Extract the dictionary and dimensions from the HotSpotConfig object
        cfg = config._cfg
        width = config._flp_cfg._width
        height = config._flp_cfg._height

        s_sp = cfg["s_spreader"]
        t_sp = cfg["t_spreader"]
        s_sk = cfg["s_sink"]
        t_sk = cfg["t_sink"]
        c_cv = cfg["c_convec"]
        p_sk = cfg["p_sink"]
        p_sp = cfg["p_spreader"]
        s_sub = cfg["s_sub"]
        t_sub = cfg["t_sub"]
        s_sol = cfg["s_solder"]
        t_sol = cfg["t_solder"]
        s_pcb = cfg["s_pcb"]
        t_pcb = cfg["t_pcb"]
        c_cv_sec = cfg.get("c_convec_sec", 140.4)

        # Primary path C
        self.c_sp_per_x = get_capacitance(p_sp, t_sp, (s_sp + height) * (s_sp - width) / 4.0)
        self.c_sp_per_y = get_capacitance(p_sp, t_sp, (s_sp + width) * (s_sp - height) / 4.0)
        self.c_hs_c_per_x = get_capacitance(p_sk, t_sk, (s_sp + height) * (s_sp - width) / 4.0)
        self.c_hs_c_per_y = get_capacitance(p_sk, t_sk, (s_sp + width) * (s_sp - height) / 4.0)
        self.c_hs_per = get_capacitance(p_sk, t_sk, (s_sk * s_sk - s_sp * s_sp) / 4.0)

        self.c_amb_c_per_x = C_FACTOR * c_cv / (s_sk * s_sk) * ((s_sp + height) * (s_sp - width) / 4.0)
        self.c_amb_c_per_y = C_FACTOR * c_cv / (s_sk * s_sk) * ((s_sp + width) * (s_sp - height) / 4.0)
        self.c_amb_per = C_FACTOR * c_cv / (s_sk * s_sk) * ((s_sk * s_sk - s_sp * s_sp) / 4.0)

        # Secondary path C
        self.c_sub_per_x = get_capacitance(SPEC_HEAT_SUB, t_sub, (s_sub + height) * (s_sub - width) / 4.0)
        self.c_sub_per_y = get_capacitance(SPEC_HEAT_SUB, t_sub, (s_sub + width) * (s_sub - height) / 4.0)
        self.c_solder_per_x = get_capacitance(SPEC_HEAT_SOLDER, t_sol, (s_sol + height) * (s_sol - width) / 4.0)
        self.c_solder_per_y = get_capacitance(SPEC_HEAT_SOLDER, t_sol, (s_sol + width) * (s_sol - height) / 4.0)
        self.c_pcb_c_per_x = get_capacitance(SPEC_HEAT_PCB, t_pcb, (s_sol + height) * (s_sol - width) / 4.0)
        self.c_pcb_c_per_y = get_capacitance(SPEC_HEAT_PCB, t_pcb, (s_sol + width) * (s_sol - height) / 4.0)
        self.c_pcb_per = get_capacitance(SPEC_HEAT_PCB, t_pcb, (s_pcb * s_pcb - s_sol * s_sol) / 4.0)

        self.c_amb_sec_c_per_x = C_FACTOR * c_cv_sec / (s_pcb * s_pcb) * ((s_sol + height) * (s_sol - width) / 4.0)
        self.c_amb_sec_c_per_y = C_FACTOR * c_cv_sec / (s_pcb * s_pcb) * ((s_sol + width) * (s_sol - height) / 4.0)
        self.c_amb_sec_per = C_FACTOR * c_cv_sec / (s_pcb * s_pcb) * ((s_pcb * s_pcb - s_sol * s_sol) / 4.0)

