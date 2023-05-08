import pandas as pd
import json


class user_profile:
    def __init__(self, subs, creat, vend, acc, payer, cat_x, item_x):
        """creates the user profile (feature-set) for recommendation """
        self.subs = subs
        self.creat = creat
        self.vend = vend
        self.acc = acc
        self.payer = payer
        self.df_final = pd.read_csv('result.csv')
        self.cat_x = cat_x - 1  # top-X most probable categories to take, minus 1 to slice the array pandas way
        self.item_x = item_x - 1  # top-X most probable items per category to take, minus 1 to slice the array pandas way
        self.vend_x = 5  # top-X most probable vendors to select for G and H

    def get_recommendation(self):
        """takes the user profile and calls a function to define the logic of recomendation system.
        Calls the appropriate function to get recommendations based on selected logic
        Returns several lists of items to recommend and their reasons
        Returns fatal error if customer is not found"""

        model = self.__select_logic()

        # for every model call the appropriate function depending on return from select_logic()
        if model == 'A':
            #### A full_rec topx_subsidiary_recommendations_for_vendor topx_payer_recommendations_for_vendor
            result1 = self.__full_recommendations()
            result2 = self.__topx_subsidiary_recommendations_for_vendor()
            result3 = self.__topx_payer_recommendations_for_vendor()
            print('model selection A')

        elif model == 'B':
            #### B topx_full topx_subsidiary_recommendations_for_vendor topx_payer_recommendations_for_vendor
            result1 = self.__topx_full_recommendations()
            result2 = self.__topx_subsidiary_recommendations_for_vendor()
            result3 = self.__topx_payer_recommendations_for_vendor()
            print('model selection B')

        elif model == 'C':
            #### C all_full topx_subsidiary_recommendations_for_vendor topx_payer_recommendations_for_vendor
            result1 = self.__topx_full_recommendations()
            result2 = self.__topx_subsidiary_recommendations_for_vendor()
            result3 = self.__topx_payer_recommendations_for_vendor()
            print('model selection C')

        elif model == 'D':
            #### D short_rec topx_subsidiary_recommendations_for_vendor topx_payer_recommendations_for_vendor
            result1 = self.__short_recommendations()
            result2 = self.__topx_subsidiary_recommendations_for_vendor()
            result3 = self.__topx_payer_recommendations_for_vendor()
            print('model selection D')

        elif model == 'E':
            #### E topx_short topx_subsidiary_recommendations_for_vendor topx_payer_recommendations_for_vendor
            result1 = self.__topx_short_recommendations()
            result2 = self.__topx_subsidiary_recommendations_for_vendor()
            result3 = self.__topx_payer_recommendations_for_vendor()
            print('model selection E')

        elif model == 'F':
            #### F all_short_rec topx_subsidiary_recommendations_for_vendor topx_payer_recommendations_for_vendor
            result1 = self.__all_short_recommendations()
            result2 = self.__topx_subsidiary_recommendations_for_vendor()
            result3 = self.__topx_payer_recommendations_for_vendor()
            print('model selection F')

        elif model == 'G':
            #### G vendor_items_payer vendor_items_subs vendor_items_acc
            result1 = self.__vendor_items_acc()
            result2 = self.__vendor_items_subs()
            result3 = self.__vendor_items_payer()
            print('model selection G')

        elif model == 'H':
            #### H vendor_items_payer vendor_items_subs
            result1 = None
            result2 = self.__vendor_items_subs()
            result3 = self.__vendor_items_payer()
            print('model selection H')

        elif model == 'ZERO':
            ### payer not found
            result1 = "Customer not in DB. Fatal ERROR!"
            result2 = "Customer not in DB. Fatal ERROR!"
            result3 = "Customer not in DB. Fatal ERROR!"

        return json.dumps([result1, result2, result3])

    def __select_logic(self):
        """Takes user profile and defines the logic for recomendations
        Returns the letter from A to H defining the recommendation system
        as per the block-diagram """

        if self.payer not in self.df_final['payer'].unique():
            # 1 payer not known, we can't recommend anything
            return 'ZERO'

        else:
            # 2 payer known
            if self.creat not in self.df_final['creator'].unique():
                # 4 user not known, we can recomment only for the subsidiary or payer
                #
                # currently 4 and 6 are pointing to the same selection, but I leave it as is to have
                # ability to split later if needed.
                # done for flexibility purposes
                #                 print("user not in DB, can suggest only customer-wide items")
                df_payer = self.df_final[self.df_final['payer'] == self.payer]

                if self.acc not in df_payer['item_account'].unique():
                    # 18 account not present for this customer
                    return 'H'

                else:
                    # 17 account present for this customer
                    return 'G'

            else:
                # 3 user known
                df_user = self.df_final[(self.df_final['creator'] == self.creat)]

                if self.vend not in df_user['vendor'].unique():
                    # 6 vendor not known for this user
                    #                     print('payer, user are in DB, but the vendor was never used by the user')
                    df_payer = self.df_final[self.df_final['payer'] == self.payer]

                    if self.acc not in df_payer['item_account'].unique():
                        # 18 account not present for this customer
                        return 'H'

                    else:
                        # 17 account present for this customer
                        return 'G'

                else:
                    # 5 vendor known for this user
                    df_vend = df_user[df_user['vendor'] == self.vend]

                    if self.acc not in df_vend['item_account'].unique():
                        # 8 account not known for this user-vendor, we recommend based on user-subsidiary-vendor features
                        #                         print("Expense account not in DB, will suggest based on user-vendor combinations")
                        feat = self.creat + self.subs + self.vend

                        if df_vend.loc[df_vend[df_vend['features_short'] == feat].index, \
                                'behavior_short'].unique() == 'frequent_focused':
                            # 13 this user-subs-vendor is frequent focused behavior
                            return 'D'

                        else:
                            # 16 this user-subs-vendor is NOT frequent focused behavior
                            if df_vend.loc[df_vend[df_vend['features_short'] == feat].index, \
                                    'behavior_short'].unique() == 'frequent_unfocused':

                                # 14 this user-subs-vendor is frequent unfocused behavior
                                return 'E'

                            else:
                                # this user-subs-vendor is occasional behavior
                                return 'F'

                    else:
                        # 7 account known for user-vendor
                        df_acc = df_vend[df_vend['item_account'] == self.acc]
                        feat = self.subs + self.creat + self.vend + self.acc

                        if df_acc.loc[df_acc[df_acc['features'] == feat].index, \
                                'behavior'].unique() == 'frequent_focused':
                            # 9 this user-subs-vendor-acc is frequent focused behavior
                            return 'A'

                        else:
                            # 10 this user-subs-vendor-acc is NOT frequent focused behavior
                            if df_acc.loc[df_acc[df_acc['features'] == feat].index, \
                                    'behavior'].unique() == 'frequent_unfocused':
                                # 11 this user-subs-vendor-acc is frequent unfocused behavior
                                return 'B'

                            else:
                                # 12 this user-subs-vendor-acc is NOT frequent unfocused behavior
                                return 'C'

    ### functions for the recommendation models

    def __full_recommendations(self):
        """Function to get most probable item name
        Takes the subsidiaryID, creatorID, accountID and vendorID
        Returns category, subcategory and item name"""
        feat = self.subs + self.creat + self.vend + self.acc

        # dataset to find the most probable category-subcategory
        df_filtered = self.df_final[(self.df_final['features'] == feat)].groupby(['features', \
                                                                                  'sub_label', 're_label']).size(). \
            to_frame('num_combinations').reset_index().sort_values(by='num_combinations', ascending=False). \
            reset_index(drop=True)

        df_filtered['probability'] = (df_filtered['num_combinations'] / df_filtered['num_combinations']. \
                                      sum() * 100).astype(int)

        # dataset to find the most probable item based on category-subcategory found previously
        df_filtered_items = self.df_final[(self.df_final['features'] == feat) & \
                                          (self.df_final['sub_label'] == df_filtered.loc[0, 'sub_label']) & \
                                          (self.df_final['re_label'] == df_filtered.loc[0, 're_label'])
                                          ].reset_index(drop=True).groupby('item_name_clean').size().to_frame(
            'number_items'). \
            sort_values(by='number_items', ascending=False).reset_index()

        result = []
        result_item = []
        result_item.append([df_filtered.loc[0, 're_label'], \
                            df_filtered.loc[0, 'sub_label'], \
                            df_filtered_items.loc[0, 'item_name_clean']])
        result.append(result_item[0])
        return result

    def __topx_subsidiary_recommendations_for_vendor(self):
        """Function to get most probable item names for the subsidiary of the creator for specified vendor
        Takes the subsidiaryID, and vendorID
        Returns top5 categorie, subcategories and top-5 item names per each"""
        df_filtered = self.df_final[(self.df_final['subsidiary'] == self.subs) & \
                                    (self.df_final['vendor'] == self.vend)]. \
            groupby(['subsidiary', 'vendor', 'sub_label', 're_label']).size(). \
            to_frame('num_combinations').reset_index().sort_values(by='num_combinations', ascending=False). \
            reset_index(drop=True)
        result = []
        category_list = df_filtered.loc[:self.cat_x, 're_label'].unique()
        subcategory_list = df_filtered.loc[:self.cat_x, 'sub_label'].unique()
        for cat in category_list:
            for subcat in subcategory_list:
                df_filtered_items = self.df_final[(self.df_final['subsidiary'] == self.subs) & \
                                                  (self.df_final['vendor'] == self.vend) &
                                                  (self.df_final['sub_label'] == subcat) & \
                                                  (self.df_final['re_label'] == cat)
                                                  ].reset_index(drop=True).groupby('item_name_clean').size().to_frame(
                    'number_items'). \
                    sort_values(by='number_items', ascending=False).reset_index()

                items_list = df_filtered_items.loc[:self.item_x, 'item_name_clean']

                for item in items_list:
                    try:
                        result_item = []
                        result_item.append([cat, subcat, item])
                        result.append(result_item[0])
                    except:
                        pass

        return result

    def __topx_payer_recommendations_for_vendor(self):
        """Function to get most probable item names for the subsidiary of the creator for specified vendor
        Takes the subsidiaryID, and vendorID
        Returns top5 categorie, subcategories and top-5 item names per each"""
        df_filtered = self.df_final[(self.df_final['payer'] == self.payer) & \
                                    (self.df_final['vendor'] == self.vend)]. \
            groupby(['payer', 'vendor', 'sub_label', 're_label']).size(). \
            to_frame('num_combinations').reset_index().sort_values(by='num_combinations', ascending=False). \
            reset_index(drop=True)
        result = []
        category_list = df_filtered.loc[:self.cat_x, 're_label'].unique()
        subcategory_list = df_filtered.loc[:self.cat_x, 'sub_label'].unique()
        for cat in category_list:
            for subcat in subcategory_list:
                df_filtered_items = self.df_final[(self.df_final['payer'] == self.payer) & \
                                                  (self.df_final['vendor'] == self.vend) &
                                                  (self.df_final['sub_label'] == subcat) & \
                                                  (self.df_final['re_label'] == cat)
                                                  ].reset_index(drop=True).groupby('item_name_clean').size().to_frame(
                    'number_items'). \
                    sort_values(by='number_items', ascending=False).reset_index()
                items_list = df_filtered_items.loc[:self.item_x, 'item_name_clean']
                for item in items_list:
                    try:
                        result_item = []
                        result_item.append([cat, subcat, item])
                        result.append(result_item[0])
                    except:
                        pass
        return result

    def __topx_full_recommendations(self):
        """Function to get most probable item name
        Takes the subsidiaryID, creatorID, acountID and vendorID
        Returns top5 categorie, subcategories and top-5 item names per each"""
        feat = self.subs + self.creat + self.vend + self.acc

        # dataset to find the most probable category-subcategory

        df_filtered = self.df_final[(self.df_final['features'] == feat)].groupby(['features', \
                                                                                  'sub_label', 're_label']).size(). \
            to_frame('num_combinations').reset_index().sort_values(by='num_combinations', ascending=False). \
            reset_index(drop=True)

        result = []
        category_list = df_filtered.loc[:self.cat_x, 're_label'].unique()
        subcategory_list = df_filtered.loc[:self.cat_x, 'sub_label'].unique()
        for cat in category_list:
            for subcat in subcategory_list:
                df_filtered_items = self.df_final[(self.df_final['features'] == feat) & \
                                                  (self.df_final['sub_label'] == subcat) & \
                                                  (self.df_final['re_label'] == cat)
                                                  ].reset_index(drop=True).groupby('item_name_clean').size().to_frame(
                    'number_items'). \
                    sort_values(by='number_items', ascending=False).reset_index()

                items_list = df_filtered_items.loc[:self.item_x, 'item_name_clean']
                for item in items_list:
                    try:
                        result_item = []
                        result_item.append([cat, subcat, item])
                        result.append(result_item[0])
                    except:
                        pass
        return result

    def __all_full_recommendations(self):
        """Function to get most probable item name
        Takes the subsidiaryID, creatorID, acountID and vendorID
        Returns top5 categorie, subcategories and top-5 item names per each"""
        feat = self.subs + self.creat + self.vend + self.acc

        # dataset to find the most probable category-subcategory

        df_filtered = self.df_final[(self.df_final['features'] == self.feat)].groupby(['features', \
                                                                                       'sub_label', 're_label']).size(). \
            to_frame('num_combinations').reset_index().sort_values(by='num_combinations', ascending=False). \
            reset_index(drop=True)

        result = []
        category_list = df_filtered.loc[:, 're_label'].unique()
        subcategory_list = df_filtered.loc[:, 'sub_label'].unique()
        for cat in category_list:
            for subcat in subcategory_list:
                df_filtered_items = self.df_final[(self.df_final['features'] == self.feat) & \
                                                  (self.df_final['sub_label'] == subcat) & \
                                                  (self.df_final['re_label'] == cat)
                                                  ].reset_index(drop=True).groupby('item_name_clean').size().to_frame(
                    'number_items'). \
                    sort_values(by='number_items', ascending=False).reset_index()

                items_list = df_filtered_items.loc[:self.item_x, 'item_name_clean']
                for item in items_list:
                    try:
                        result_item = []
                        result_item.append([cat, subcat, item])
                        result.append(result_item[0])
                    except:
                        pass
        return result

    def __short_recommendations(self):
        """Function to get most probable item name
        Takes the subsidiaryID, creatorID and vendorID
        Returns category, subcategory and item name"""
        feat = self.creat + self.subs + self.vend

        # dataset to find the most probable category-subcategory

        df_filtered = self.df_final[(self.df_final['features_short'] == feat)].groupby(['features_short', \
                                                                                        'sub_label',
                                                                                        're_label']).size(). \
            to_frame('num_combinations').reset_index().sort_values(by='num_combinations', ascending=False). \
            reset_index(drop=True)

        # dataset to find the most probable item based on category-subcategory found previously
        df_filtered_items = self.df_final[(self.df_final['features_short'] == feat) & \
                                          (self.df_final['sub_label'] == df_filtered.loc[0, 'sub_label']) & \
                                          (self.df_final['re_label'] == df_filtered.loc[0, 're_label'])
                                          ].reset_index(drop=True).groupby('item_name_clean').size().to_frame(
            'number_items'). \
            sort_values(by='number_items', ascending=False).reset_index()

        result = []
        result_item = []
        result_item.append([df_filtered.loc[0, 're_label'], \
                            df_filtered.loc[0, 'sub_label'], \
                            df_filtered_items.loc[0, 'item_name_clean']])
        result.append(result_item[0])
        return result

    def __topx_short_recommendations(self):
        """Function to get most probable item name
        Takes the subsidiaryID, creatorID and vendorID
        Returns top5 categorie, subcategories and top-5 item names per each"""
        feat = self.creat + self.subs + self.vend

        # dataset to find the most probable category-subcategory

        df_filtered = self.df_final[(self.df_final['features_short'] == feat)].groupby(['features_short', \
                                                                                        'sub_label',
                                                                                        're_label']).size(). \
            to_frame('num_combinations').reset_index().sort_values(by='num_combinations', ascending=False). \
            reset_index(drop=True)

        # dataset to find the most probable item based on category-subcategory found previously
        result = []
        category_list = df_filtered.loc[:self.cat_x, 're_label'].unique()
        subcategory_list = df_filtered.loc[:self.cat_x, 'sub_label'].unique()
        for cat in category_list:
            for subcat in subcategory_list:
                df_filtered_items = self.df_final[(self.df_final['features_short'] == feat) & \
                                                  (self.df_final['sub_label'] == subcat) & \
                                                  (self.df_final['re_label'] == cat)
                                                  ].reset_index(drop=True).groupby('item_name_clean').size().to_frame(
                    'number_items'). \
                    sort_values(by='number_items', ascending=False).reset_index()

                items_list = df_filtered_items.loc[:self.item_x, 'item_name_clean']
                for item in items_list:
                    try:
                        result_item = []
                        result_item.append([cat, subcat, item])
                        result.append(result_item[0])
                    except:
                        pass
        return result

    def __all_short_recommendations(self):
        """Function to get most probable item name
        Takes the subsidiaryID, creatorID and vendorID
        Returns top5 categorie, subcategories and top-5 item names per each"""
        feat = self.creat + self.subs + self.vend

        # dataset to find the most probable category-subcategory

        df_filtered = self.df_final[(self.df_final['features_short'] == feat)].groupby(['features_short', \
                                                                                        'sub_label',
                                                                                        're_label']).size(). \
            to_frame('num_combinations').reset_index().sort_values(by='num_combinations', ascending=False). \
            reset_index(drop=True)

        # dataset to find the most probable item based on category-subcategory found previously
        result = []
        category_list = df_filtered.loc[:, 're_label'].unique()
        subcategory_list = df_filtered.loc[:, 'sub_label'].unique()
        for cat in category_list:
            for subcat in subcategory_list:
                df_filtered_items = self.df_final[(self.df_final['features_short'] == feat) & \
                                                  (self.df_final['sub_label'] == subcat) & \
                                                  (self.df_final['re_label'] == cat)
                                                  ].reset_index(drop=True).groupby('item_name_clean').size().to_frame(
                    'number_items'). \
                    sort_values(by='number_items', ascending=False).reset_index()

                items_list = df_filtered_items.loc[:, 'item_name_clean']
                for item in items_list:
                    try:
                        result_item = []
                        result_item.append([cat, subcat, item])
                        result.append(result_item[0])
                    except:
                        pass
        return result

    def __vendor_items_acc(self):
        """Function to get most probable item name
        Takes the subsidiaryID, payerID, accountID
        Returns top5 categorie, subcategories and top-5 item names per each forsubsidiary-account"""

        vendor_list = self.df_final[(self.df_final['subsidiary'] == self.subs) & \
                                    (self.df_final['item_account'] == self.acc)].groupby('vendor'). \
                          size().to_frame('amount').sort_values(by='amount', ascending=False).reset_index().loc[
                      :self.vend_x, 'vendor']
        df_filtered = self.df_final[(self.df_final['vendor'].isin(vendor_list)) & \
                                    (self.df_final['subsidiary'] == self.subs)]. \
            groupby(['re_label', 'sub_label']).size().to_frame('amount').sort_values(by='amount', ascending=False). \
            reset_index()

        result = []
        category_list = df_filtered.loc[:self.cat_x, 're_label'].unique()
        subcategory_list = df_filtered.loc[:self.cat_x, 'sub_label'].unique()
        for cat in category_list:
            for subcat in subcategory_list:
                for vendor in vendor_list:
                    df_filtered_items = self.df_final[(self.df_final['subsidiary'] == self.subs) & \
                                                      (self.df_final['vendor'] == vendor) & \
                                                      (self.df_final['item_account'] == self.acc) & \
                                                      (self.df_final['sub_label'] == subcat) & \
                                                      (self.df_final['re_label'] == cat)].reset_index(drop=True). \
                        groupby('item_name_clean').size().to_frame('number_items'). \
                        sort_values(by='number_items', ascending=False).reset_index()

                    items_list = df_filtered_items.loc[:self.item_x, 'item_name_clean']
                    for item in items_list:
                        try:
                            result_item = []
                            result_item.append([cat, subcat, item])
                            result.append(result_item[0])
                        except:
                            pass
        return result

    def __vendor_items_subs(self):
        """Function to get most probable item names
        Takes the subsidiaryID, payerID,
        Returns top5 categorie, subcategories and top-5 item names per each for the subsidiary"""

        vendor_list = self.df_final[(self.df_final['subsidiary'] == self.subs)].groupby('vendor'). \
                          size().to_frame('amount').sort_values(by='amount', ascending=False).reset_index().loc[
                      :self.vend_x, 'vendor']
        df_filtered = self.df_final[(self.df_final['vendor'].isin(vendor_list)) & \
                                    (self.df_final['subsidiary'] == self.subs)]. \
            groupby(['re_label', 'sub_label']).size().to_frame('amount').sort_values(by='amount', ascending=False). \
            reset_index()

        result = []
        category_list = df_filtered.loc[:self.cat_x, 're_label'].unique()
        subcategory_list = df_filtered.loc[:self.cat_x, 'sub_label'].unique()
        for cat in category_list:
            for subcat in subcategory_list:
                for vendor in vendor_list:
                    df_filtered_items = self.df_final[(self.df_final['subsidiary'] == self.subs) & \
                                                      (self.df_final['vendor'] == vendor) &
                                                      (self.df_final['sub_label'] == subcat) & (
                                                                  self.df_final['re_label'] == cat)]. \
                        reset_index(drop=True). \
                        groupby('item_name_clean').size().to_frame('number_items'). \
                        sort_values(by='number_items', ascending=False).reset_index()

                    items_list = df_filtered_items.loc[:self.item_x, 'item_name_clean']
                    for item in items_list:
                        try:
                            result_item = []
                            result_item.append([cat, subcat, item])
                            result.append(result_item[0])
                        except:
                            pass
        return result

    def __vendor_items_payer(self):
        """Function to get most probable item names
        Takes the payerID,
        Returns top5 categorie, subcategories and top-5 item names per each for the payer"""

        vendor_list = self.df_final[(self.df_final['payer'] == self.payer)].groupby('vendor'). \
                          size().to_frame('amount').sort_values(by='amount', ascending=False).reset_index().loc[
                      :self.vend_x, 'vendor']
        df_filtered = self.df_final[(self.df_final['vendor'].isin(vendor_list)) & \
                                    (self.df_final['payer'] == self.payer)].groupby(['re_label', 'sub_label']). \
            size().to_frame('amount').sort_values(by='amount', ascending=False).reset_index()

        result = []
        category_list = df_filtered.loc[:self.cat_x, 're_label'].unique()
        subcategory_list = df_filtered.loc[:self.cat_x, 'sub_label'].unique()
        for cat in category_list:
            for subcat in subcategory_list:
                for vendor in vendor_list:
                    df_filtered_items = self.df_final[(self.df_final['payer'] == self.payer) & \
                                                      (self.df_final['vendor'] == self.vend) &
                                                      (self.df_final['sub_label'] == subcat) & \
                                                      (self.df_final['re_label'] == cat)].reset_index(drop=True). \
                        groupby('item_name_clean').size().to_frame('number_items'). \
                        sort_values(by='number_items', ascending=False).reset_index()

                    items_list = df_filtered_items.loc[:self.item_x, 'item_name_clean']
                    for item in items_list:
                        try:
                            result_item = []
                            result_item.append([cat, subcat, item])
                            result.append(result_item[0])
                        except:
                            pass
        return result